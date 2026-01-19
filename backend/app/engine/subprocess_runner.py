"""
Subprocess Code Executor - 在独立子进程中执行 Python 代码

特点：
- 进程隔离：代码崩溃不影响主服务
- 超时控制：可设置执行时间限制
- 第三方库：支持使用更多库（如 numpy, pandas）
- 资源限制：可以限制内存使用（Windows 上有限）

适用场景：
- 长时间运行的计算
- 需要第三方库的代码
- 需要严格隔离的代码
"""
import subprocess
import sys
import os
import json
import tempfile
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.core.logger import logger


@dataclass
class SubprocessResult:
    """子进程执行结果"""
    success: bool
    result: Any
    stdout: str
    stderr: str
    execution_time_ms: int
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    return_code: Optional[int] = None


# 包装器代码模板
WRAPPER_TEMPLATE = '''
import sys
import json
import traceback

# 读取上下文
context = json.loads(sys.stdin.read())

# 捕获 stdout
import io
from contextlib import redirect_stdout

stdout_capture = io.StringIO()

try:
    # 用户代码
{user_code}
    
    # 检查并执行 main 函数
    if 'main' not in dir():
        raise ValueError("Code must define a 'main(context)' function")
    
    with redirect_stdout(stdout_capture):
        result = main(context)
    
    # 尝试 JSON 序列化结果
    try:
        json.dumps(result)
        serializable_result = result
    except (TypeError, ValueError):
        serializable_result = str(result)
    
    output = {{
        "success": True,
        "result": serializable_result,
        "stdout": stdout_capture.getvalue()
    }}
    print(json.dumps(output))
    
except Exception as e:
    output = {{
        "success": False,
        "result": None,
        "stdout": stdout_capture.getvalue(),
        "error_message": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(output))
'''


def get_python_executable() -> str:
    """
    获取 Python 解释器路径
    
    优先使用项目 venv，如果不存在则使用系统 Python
    """
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Windows venv 路径
    venv_python = os.path.join(project_root, '.venv', 'Scripts', 'python.exe')
    
    if os.path.exists(venv_python):
        return venv_python
    
    # Unix venv 路径
    venv_python_unix = os.path.join(project_root, '.venv', 'bin', 'python')
    if os.path.exists(venv_python_unix):
        return venv_python_unix
    
    # 回退到当前 Python
    return sys.executable


def indent_code(code: str, spaces: int = 4) -> str:
    """为代码添加缩进"""
    lines = code.split('\n')
    indented_lines = [' ' * spaces + line if line.strip() else line for line in lines]
    return '\n'.join(indented_lines)


def execute_in_subprocess(
    code_content: str,
    context: Dict[str, Any],
    timeout_seconds: int = 30,
    python_path: Optional[str] = None,
    allowed_imports: Optional[list] = None
) -> SubprocessResult:
    """
    在独立子进程中执行 Python 代码
    
    Args:
        code_content: Python 代码字符串
        context: 传递给代码的上下文数据
        timeout_seconds: 执行超时时间（秒）
        python_path: Python 解释器路径（默认使用项目 venv）
        allowed_imports: 允许导入的模块列表（暂未实现白名单检查）
        
    Returns:
        SubprocessResult 包含执行结果
        
    Example:
        result = execute_in_subprocess(
            code_content='def main(ctx): return ctx["x"] * 2',
            context={"x": 5},
            timeout_seconds=10
        )
    """
    start_time = time.time()
    
    # 获取 Python 解释器
    if python_path is None:
        python_path = get_python_executable()
    
    logger.info(f"Subprocess execution with Python: {python_path}")
    logger.debug(f"Code length: {len(code_content)} chars, timeout: {timeout_seconds}s")
    
    # 构建包装器代码
    indented_code = indent_code(code_content)
    wrapper_code = WRAPPER_TEMPLATE.format(user_code=indented_code)
    
    try:
        # 将上下文序列化为 JSON
        context_json = json.dumps(context, ensure_ascii=False, default=str)
        
        # 启动子进程
        proc = subprocess.run(
            [python_path, '-c', wrapper_code],
            input=context_json,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=os.getcwd(),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # 解析输出
        stdout_content = proc.stdout
        stderr_content = proc.stderr
        
        if proc.returncode == 0 and stdout_content.strip():
            try:
                # 尝试解析 JSON 输出
                output = json.loads(stdout_content.strip().split('\n')[-1])
                
                if output.get("success"):
                    return SubprocessResult(
                        success=True,
                        result=output.get("result"),
                        stdout=output.get("stdout", ""),
                        stderr=stderr_content,
                        execution_time_ms=execution_time_ms,
                        return_code=proc.returncode
                    )
                else:
                    return SubprocessResult(
                        success=False,
                        result=None,
                        stdout=output.get("stdout", ""),
                        stderr=stderr_content,
                        execution_time_ms=execution_time_ms,
                        error_message=output.get("error_message"),
                        error_type=output.get("error_type"),
                        return_code=proc.returncode
                    )
            except json.JSONDecodeError:
                # 无法解析 JSON，返回原始输出
                return SubprocessResult(
                    success=False,
                    result=None,
                    stdout=stdout_content,
                    stderr=stderr_content,
                    execution_time_ms=execution_time_ms,
                    error_message="Failed to parse execution output as JSON",
                    error_type="JSONDecodeError",
                    return_code=proc.returncode
                )
        else:
            # 进程失败
            return SubprocessResult(
                success=False,
                result=None,
                stdout=stdout_content,
                stderr=stderr_content,
                execution_time_ms=execution_time_ms,
                error_message=stderr_content or f"Process exited with code {proc.returncode}",
                error_type="SubprocessError",
                return_code=proc.returncode
            )
            
    except subprocess.TimeoutExpired:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.warning(f"Subprocess execution timed out after {timeout_seconds}s")
        return SubprocessResult(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            error_message=f"Execution timed out after {timeout_seconds} seconds",
            error_type="TimeoutError"
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Subprocess execution failed: {e}")
        return SubprocessResult(
            success=False,
            result=None,
            stdout="",
            stderr=str(e),
            execution_time_ms=execution_time_ms,
            error_message=str(e),
            error_type=type(e).__name__
        )


def execute_with_file(
    code_content: str,
    context: Dict[str, Any],
    timeout_seconds: int = 30,
    python_path: Optional[str] = None
) -> SubprocessResult:
    """
    使用临时文件执行代码（适用于较长的代码）
    
    与 execute_in_subprocess 类似，但将代码写入临时文件而不是通过 -c 参数传递。
    这种方式对于较长的代码更可靠。
    
    Args:
        code_content: Python 代码字符串
        context: 传递给代码的上下文数据
        timeout_seconds: 执行超时时间（秒）
        python_path: Python 解释器路径
        
    Returns:
        SubprocessResult 包含执行结果
    """
    start_time = time.time()
    
    if python_path is None:
        python_path = get_python_executable()
    
    logger.info(f"Subprocess execution (file mode) with Python: {python_path}")
    
    # 构建包装器代码
    indented_code = indent_code(code_content)
    wrapper_code = WRAPPER_TEMPLATE.format(user_code=indented_code)
    
    temp_file = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(wrapper_code)
            temp_file = f.name
        
        # 将上下文序列化为 JSON
        context_json = json.dumps(context, ensure_ascii=False, default=str)
        
        # 启动子进程
        proc = subprocess.run(
            [python_path, temp_file],
            input=context_json,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=os.getcwd(),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # 解析输出（与 execute_in_subprocess 相同的逻辑）
        stdout_content = proc.stdout
        stderr_content = proc.stderr
        
        if proc.returncode == 0 and stdout_content.strip():
            try:
                output = json.loads(stdout_content.strip().split('\n')[-1])
                
                if output.get("success"):
                    return SubprocessResult(
                        success=True,
                        result=output.get("result"),
                        stdout=output.get("stdout", ""),
                        stderr=stderr_content,
                        execution_time_ms=execution_time_ms,
                        return_code=proc.returncode
                    )
                else:
                    return SubprocessResult(
                        success=False,
                        result=None,
                        stdout=output.get("stdout", ""),
                        stderr=stderr_content,
                        execution_time_ms=execution_time_ms,
                        error_message=output.get("error_message"),
                        error_type=output.get("error_type"),
                        return_code=proc.returncode
                    )
            except json.JSONDecodeError:
                return SubprocessResult(
                    success=False,
                    result=None,
                    stdout=stdout_content,
                    stderr=stderr_content,
                    execution_time_ms=execution_time_ms,
                    error_message="Failed to parse execution output",
                    error_type="JSONDecodeError",
                    return_code=proc.returncode
                )
        else:
            return SubprocessResult(
                success=False,
                result=None,
                stdout=stdout_content,
                stderr=stderr_content,
                execution_time_ms=execution_time_ms,
                error_message=stderr_content or f"Process exited with code {proc.returncode}",
                error_type="SubprocessError",
                return_code=proc.returncode
            )
            
    except subprocess.TimeoutExpired:
        execution_time_ms = int((time.time() - start_time) * 1000)
        return SubprocessResult(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=execution_time_ms,
            error_message=f"Execution timed out after {timeout_seconds} seconds",
            error_type="TimeoutError"
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        return SubprocessResult(
            success=False,
            result=None,
            stdout="",
            stderr=str(e),
            execution_time_ms=execution_time_ms,
            error_message=str(e),
            error_type=type(e).__name__
        )
        
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")
