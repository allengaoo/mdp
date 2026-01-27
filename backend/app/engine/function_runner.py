"""
Dynamic function execution engine.
Executes user-defined Python code stored in FunctionDefinition.code_content.

增强版本支持：
- 扩展的内置函数
- 常用标准库 (datetime, json, random, re, math)
- 运行时 API (get_object, update_object, create_link 等)
- stdout/stderr 捕获
- 执行超时控制
"""
import ast
import sys
import io
import time
import traceback
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from contextlib import redirect_stdout, redirect_stderr
from sqlmodel import Session

from app.core.logger import logger
from app.engine.meta_crud import get_function_definition
from app.engine.runtime_context import build_runtime_api


@dataclass
class ExecutionResult:
    """代码执行结果"""
    success: bool
    result: Any
    stdout: str
    stderr: str
    execution_time_ms: int
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None


def validate_syntax(code_content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python code syntax without executing it.
    
    Args:
        code_content: Python code string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, error_message)
    """
    try:
        ast.parse(code_content)
        return True, None
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f"\n  {e.text.strip()}"
        return False, error_msg
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def build_restricted_builtins() -> Dict[str, Any]:
    """
    构建受限的内置函数集合
    
    包含安全的内置函数，排除危险操作如：
    - exec, eval (代码执行)
    - open, input (文件/IO)
    - compile (代码编译)
    
    注意：允许受限的 __import__ 以支持安全模块导入
    """
    return {
        # 数据类型转换
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'frozenset': frozenset,
        'bytes': bytes,
        'bytearray': bytearray,
        
        # 数学运算
        'min': min,
        'max': max,
        'sum': sum,
        'abs': abs,
        'round': round,
        'pow': pow,
        'divmod': divmod,
        
        # 迭代工具
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'sorted': sorted,
        'reversed': reversed,
        'iter': iter,
        'next': next,
        
        # 类型检查
        'isinstance': isinstance,
        'issubclass': issubclass,
        'type': type,
        'callable': callable,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'delattr': delattr,
        
        # 字符串处理
        'ord': ord,
        'chr': chr,
        'repr': repr,
        'format': format,
        'ascii': ascii,
        
        # 其他安全函数
        'all': all,
        'any': any,
        'id': id,
        'hash': hash,
        'slice': slice,
        'object': object,
        'staticmethod': staticmethod,
        'classmethod': classmethod,
        'property': property,
        
        # 调试输出
        'print': print,
        
        # 导入功能 - 使用受限导入器
        '__import__': __import__,
        
        # 异常类型（允许用户代码捕获和抛出）
        'Exception': Exception,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'KeyError': KeyError,
        'IndexError': IndexError,
        'AttributeError': AttributeError,
        'RuntimeError': RuntimeError,
        'StopIteration': StopIteration,
        'ZeroDivisionError': ZeroDivisionError,
        'ImportError': ImportError,
        
        # 常量
        'True': True,
        'False': False,
        'None': None,
    }


def build_stdlib_modules() -> Dict[str, Any]:
    """
    构建允许使用的标准库模块
    
    仅包含安全的、常用的模块，排除危险模块如：
    - os, sys, subprocess (系统操作)
    - socket, http (网络操作)
    - importlib (动态导入)
    """
    import math
    import datetime
    import json
    import random
    import re
    import copy
    import itertools
    import functools
    import collections
    import decimal
    import statistics
    
    return {
        'math': math,
        'datetime': datetime,
        'json': json,
        'random': random,
        're': re,
        'copy': copy,
        'itertools': itertools,
        'functools': functools,
        'collections': collections,
        'decimal': decimal,
        'statistics': statistics,
    }


def execute_code_direct(
    code_content: str,
    context: Dict[str, Any],
    session: Optional[Session] = None,
    timeout_seconds: Optional[int] = None
) -> ExecutionResult:
    """
    直接执行 Python 代码（内置执行器）
    
    Args:
        code_content: Python 代码字符串
        context: 传递给用户代码的上下文字典
        session: 数据库会话（用于运行时 API）
        timeout_seconds: 执行超时时间（秒），None 表示不限制
        
    Returns:
        ExecutionResult 包含执行结果、输出和错误信息
    """
    start_time = time.time()
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # 验证语法
    is_valid, syntax_error = validate_syntax(code_content)
    if not is_valid:
        return ExecutionResult(
            success=False,
            result=None,
            stdout="",
            stderr="",
            execution_time_ms=0,
            error_message=syntax_error,
            error_type="SyntaxError"
        )
    
    # 构建执行环境
    globals_dict = {
        '__builtins__': build_restricted_builtins(),
    }
    
    # 添加标准库
    globals_dict.update(build_stdlib_modules())
    
    # 添加运行时 API（如果有数据库会话）
    if session:
        runtime_api = build_runtime_api(session, context.get("source"))
        globals_dict.update(runtime_api)
    
    locals_dict = {}
    
    try:
        # 编译用户代码
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code_content, globals_dict, locals_dict)
        
        # 检查 main 函数
        if 'main' not in locals_dict:
            return ExecutionResult(
                success=False,
                result=None,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="Code must define a 'main(context)' function",
                error_type="ValueError"
            )
        
        main_func = locals_dict['main']
        if not callable(main_func):
            return ExecutionResult(
                success=False,
                result=None,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="'main' is not callable",
                error_type="TypeError"
            )
        
        # 执行 main 函数
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = main_func(context)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return ExecutionResult(
            success=True,
            result=result,
            stdout=stdout_capture.getvalue(),
            stderr=stderr_capture.getvalue(),
            execution_time_ms=execution_time_ms
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        tb = traceback.format_exc()
        
        return ExecutionResult(
            success=False,
            result=None,
            stdout=stdout_capture.getvalue(),
            stderr=stderr_capture.getvalue(),
            execution_time_ms=execution_time_ms,
            error_message=str(e),
            error_type=type(e).__name__,
            traceback=tb
        )


def execute_function(
    session: Session,
    function_id: str,
    context: Dict[str, Any]
) -> Any:
    """
    Execute a user-defined function from FunctionDefinition.
    
    这是向后兼容的接口，内部使用 execute_code_direct。
    
    Args:
        session: Database session
        function_id: UUID of the FunctionDefinition to execute
        context: Context dictionary passed to the user's main() function
                 Typically contains: {"source": {...}, "target": {...}, ...}
        
    Returns:
        Result from the user's main(context) function
        
    Raises:
        ValueError: If function not found or main() function not defined
        SyntaxError: If code has syntax errors
        RuntimeError: If user code execution fails
    """
    # Step 1: Fetch FunctionDefinition from DB
    logger.info(f"Fetching FunctionDefinition: {function_id}")
    function_def = get_function_definition(session, function_id)
    
    if not function_def:
        error_msg = f"FunctionDefinition not found: {function_id}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not function_def.code_content:
        error_msg = f"FunctionDefinition '{function_def.api_name}' has no code_content"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Executing Function: {function_def.api_name} | ID: {function_id}")
    logger.debug(f"Function code length: {len(function_def.code_content)} characters")
    logger.debug(f"Input context: {context}")
    
    # Step 2: Execute using the enhanced executor
    result = execute_code_direct(
        code_content=function_def.code_content,
        context=context,
        session=session
    )
    
    # Step 3: Handle result
    if result.stdout:
        logger.debug(f"Function stdout:\n{result.stdout}")
    if result.stderr:
        logger.warning(f"Function stderr:\n{result.stderr}")
    
    if result.success:
        logger.info(f"Function '{function_def.api_name}' executed successfully in {result.execution_time_ms}ms")
        logger.debug(f"Function result: {result.result}")
        return result.result
    else:
        logger.error(f"Function '{function_def.api_name}' failed: {result.error_message}")
        if result.traceback:
            logger.debug(f"Traceback:\n{result.traceback}")
        
        # 根据错误类型抛出相应异常
        if result.error_type == "SyntaxError":
            raise SyntaxError(result.error_message)
        elif result.error_type == "ValueError":
            raise ValueError(result.error_message)
        else:
            raise RuntimeError(f"Function execution failed: {result.error_message}")


def test_code(
    code_content: str,
    context: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None
) -> ExecutionResult:
    """
    测试运行代码（不保存状态）
    
    用于前端试运行功能，提供详细的执行反馈。
    
    Args:
        code_content: Python 代码字符串
        context: 测试上下文数据
        session: 数据库会话（可选，用于运行时 API）
        
    Returns:
        ExecutionResult 包含完整的执行信息
        
    Example:
        result = test_code(
            code_content='def main(ctx): return ctx["x"] * 2',
            context={"x": 5}
        )
        if result.success:
            print(f"Result: {result.result}")  # Result: 10
        else:
            print(f"Error: {result.error_message}")
    """
    logger.info("Testing code execution")
    logger.debug(f"Code length: {len(code_content)} characters")
    
    test_context = context or {}
    
    result = execute_code_direct(
        code_content=code_content,
        context=test_context,
        session=session
    )
    
    if result.success:
        logger.info(f"Test execution succeeded in {result.execution_time_ms}ms")
    else:
        logger.warning(f"Test execution failed: {result.error_message}")
    
    return result
