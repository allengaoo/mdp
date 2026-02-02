"""
Code Executor - 代码执行调度器

统一的代码执行入口，根据配置和代码特征选择合适的执行器：
- 内置执行器 (builtin): 快速、可访问数据库，适合简单代码
- 子进程执行器 (subprocess): 隔离、支持超时，适合复杂/长时间代码

执行模式：
- auto: 自动选择（默认）
- builtin: 强制使用内置执行器
- subprocess: 强制使用子进程执行器
"""
import re
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, asdict
from enum import Enum
from sqlmodel import Session

from app.core.logger import logger
from app.engine.function_runner import execute_code_direct, ExecutionResult, test_code
from app.engine.subprocess_runner import execute_in_subprocess, SubprocessResult
from app.engine.meta_crud import get_function_definition


class ExecutorType(str, Enum):
    """执行器类型"""
    BUILTIN = "builtin"
    SUBPROCESS = "subprocess"
    REMOTE = "remote"  # 远程沙箱执行
    AUTO = "auto"


@dataclass
class CodeExecutionRequest:
    """代码执行请求"""
    code_content: str
    context: Dict[str, Any]
    executor_type: ExecutorType = ExecutorType.AUTO
    timeout_seconds: Optional[int] = 30
    session: Optional[Session] = None


@dataclass
class CodeExecutionResponse:
    """代码执行响应"""
    success: bool
    result: Any
    stdout: str
    stderr: str
    execution_time_ms: int
    executor_used: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# 需要子进程执行的模块（因为可能有 C 扩展或需要隔离）
SUBPROCESS_REQUIRED_IMPORTS = {
    'numpy', 'np',
    'pandas', 'pd',
    'scipy',
    'sklearn', 'scikit-learn',
    'tensorflow', 'tf',
    'torch', 'pytorch',
    'cv2', 'opencv',
    'PIL', 'pillow',
    'matplotlib', 'plt',
    'seaborn', 'sns',
}

# 需要数据库访问的 API（需要内置执行器）
DATABASE_API_CALLS = {
    'get_object',
    'update_object',
    'create_object',
    'delete_object',
    'query_objects',
    'get_linked_objects',
    'create_link',
    'delete_link',
    'get_source',
    'get_object_type',
}


def detect_imports(code_content: str) -> set:
    """
    检测代码中的 import 语句
    
    Args:
        code_content: Python 代码
        
    Returns:
        导入的模块名称集合
    """
    imports = set()
    
    # 匹配 import xxx 和 from xxx import
    import_pattern = r'(?:^|\n)\s*(?:import|from)\s+(\w+)'
    matches = re.findall(import_pattern, code_content)
    imports.update(matches)
    
    return imports


def detect_database_api_usage(code_content: str) -> bool:
    """
    检测代码是否使用了数据库 API
    
    Args:
        code_content: Python 代码
        
    Returns:
        是否使用了数据库 API
    """
    for api_call in DATABASE_API_CALLS:
        if api_call in code_content:
            return True
    return False


def choose_executor(code_content: str, has_session: bool) -> ExecutorType:
    """
    自动选择执行器类型
    
    选择逻辑：
    1. 如果使用了需要子进程的模块 → subprocess
    2. 如果使用了数据库 API 且有 session → builtin
    3. 其他情况 → builtin（更快）
    
    Args:
        code_content: Python 代码
        has_session: 是否有数据库会话
        
    Returns:
        推荐的执行器类型
    """
    imports = detect_imports(code_content)
    uses_db_api = detect_database_api_usage(code_content)
    
    # 检查是否需要子进程执行
    subprocess_imports = imports & SUBPROCESS_REQUIRED_IMPORTS
    if subprocess_imports:
        logger.info(f"Detected imports requiring subprocess: {subprocess_imports}")
        return ExecutorType.SUBPROCESS
    
    # 如果使用数据库 API，优先使用内置执行器
    if uses_db_api:
        if has_session:
            logger.info("Code uses database API, using builtin executor")
            return ExecutorType.BUILTIN
        else:
            logger.warning("Code uses database API but no session provided, using subprocess (API will fail)")
            return ExecutorType.SUBPROCESS
    
    # 默认使用内置执行器（更快）
    return ExecutorType.BUILTIN


def execute_in_sandbox(
    code_content: str,
    context: Dict[str, Any],
    timeout_seconds: int = 30,
    sandbox_url: Optional[str] = None
) -> CodeExecutionResponse:
    """
    在远程沙箱服务中执行代码
    
    Args:
        code_content: Python 代码
        context: 执行上下文
        timeout_seconds: 超时时间
        sandbox_url: 沙箱服务 URL（默认从配置读取）
        
    Returns:
        代码执行响应
    """
    import httpx
    import time
    from app.core.config import settings
    
    start_time = time.time()
    url = sandbox_url or settings.sandbox_url
    
    logger.info(f"Executing code in remote sandbox: {url}")
    
    try:
        with httpx.Client(timeout=timeout_seconds + 10) as client:
            response = client.post(
                f"{url}/execute",
                json={
                    "code_content": code_content,
                    "context": context,
                    "timeout_seconds": timeout_seconds
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return CodeExecutionResponse(
                success=data.get("success", False),
                result=data.get("result"),
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                execution_time_ms=data.get("execution_time_ms", 0),
                executor_used="remote",
                error_message=data.get("error_message"),
                error_type=data.get("error_type"),
                traceback=data.get("traceback")
            )
    except httpx.TimeoutException:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.warning(f"Sandbox request timed out after {timeout_seconds}s")
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            executor_used="remote",
            error_message=f"Sandbox request timed out after {timeout_seconds} seconds",
            error_type="TimeoutError"
        )
    except httpx.HTTPStatusError as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Sandbox HTTP error: {e}")
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            executor_used="remote",
            error_message=f"Sandbox HTTP error: {e.response.status_code}",
            error_type="HTTPError"
        )
    except httpx.ConnectError as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Cannot connect to sandbox: {e}")
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            executor_used="remote",
            error_message=f"Cannot connect to sandbox service at {url}",
            error_type="ConnectionError"
        )
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Sandbox execution failed: {e}")
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            executor_used="remote",
            error_message=str(e),
            error_type=type(e).__name__
        )


def execute_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    """
    执行代码的统一入口
    
    Args:
        request: 代码执行请求
        
    Returns:
        代码执行响应
        
    Example:
        response = execute_code(CodeExecutionRequest(
            code_content='def main(ctx): return ctx["x"] * 2',
            context={"x": 5},
            executor_type=ExecutorType.AUTO
        ))
    """
    logger.info(f"Executing code with executor_type={request.executor_type}")
    
    # 确定执行器类型
    if request.executor_type == ExecutorType.AUTO:
        executor_type = choose_executor(
            request.code_content,
            request.session is not None
        )
    else:
        executor_type = request.executor_type
    
    logger.info(f"Using executor: {executor_type.value}")
    
    # 执行代码
    if executor_type == ExecutorType.BUILTIN:
        result = execute_code_direct(
            code_content=request.code_content,
            context=request.context,
            session=request.session,
            timeout_seconds=request.timeout_seconds
        )
        
        return CodeExecutionResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_ms=result.execution_time_ms,
            executor_used=ExecutorType.BUILTIN.value,
            error_message=result.error_message,
            error_type=result.error_type,
            traceback=result.traceback
        )
    
    elif executor_type == ExecutorType.SUBPROCESS:
        result = execute_in_subprocess(
            code_content=request.code_content,
            context=request.context,
            timeout_seconds=request.timeout_seconds or 30
        )
        
        return CodeExecutionResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_ms=result.execution_time_ms,
            executor_used=ExecutorType.SUBPROCESS.value,
            error_message=result.error_message,
            error_type=result.error_type
        )
    
    else:  # REMOTE
        return execute_in_sandbox(
            code_content=request.code_content,
            context=request.context,
            timeout_seconds=request.timeout_seconds or 30
        )


def execute_function_by_id(
    session: Session,
    function_id: str,
    context: Dict[str, Any],
    executor_type: ExecutorType = ExecutorType.AUTO,
    timeout_seconds: Optional[int] = 30
) -> CodeExecutionResponse:
    """
    根据函数 ID 执行函数
    
    Args:
        session: 数据库会话
        function_id: FunctionDefinition ID
        context: 执行上下文
        executor_type: 执行器类型
        timeout_seconds: 超时时间
        
    Returns:
        代码执行响应
    """
    # 获取函数定义
    function_def = get_function_definition(session, function_id)
    if not function_def:
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=0,
            executor_used="none",
            error_message=f"FunctionDefinition not found: {function_id}",
            error_type="ValueError"
        )
    
    if not function_def.code_content:
        return CodeExecutionResponse(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=0,
            executor_used="none",
            error_message=f"FunctionDefinition '{function_def.api_name}' has no code_content",
            error_type="ValueError"
        )
    
    logger.info(f"Executing function: {function_def.api_name} (ID: {function_id})")
    
    # 执行代码
    return execute_code(CodeExecutionRequest(
        code_content=function_def.code_content,
        context=context,
        executor_type=executor_type,
        timeout_seconds=timeout_seconds,
        session=session
    ))


def try_function_code(
    code_content: str,
    context: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None,
    executor_type: ExecutorType = ExecutorType.AUTO,
    timeout_seconds: int = 30
) -> CodeExecutionResponse:
    """
    试运行函数代码（不保存状态）
    
    用于前端试运行功能。
    
    Args:
        code_content: Python 代码
        context: 测试上下文
        session: 数据库会话（可选）
        executor_type: 执行器类型
        timeout_seconds: 超时时间
        
    Returns:
        代码执行响应
    """
    logger.info("Testing function code")
    
    return execute_code(CodeExecutionRequest(
        code_content=code_content,
        context=context or {},
        executor_type=executor_type,
        timeout_seconds=timeout_seconds,
        session=session
    ))
