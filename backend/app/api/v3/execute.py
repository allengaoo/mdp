"""
V3.1 API - Execute
Code test and function test endpoints (V3 mirror of v1 execute).
"""
from typing import Optional, Dict, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from app.core.db import get_session
from app.core.logger import logger
from app.engine.code_executor import try_function_code, ExecutorType
from app.engine.function_runner import validate_syntax

router = APIRouter(prefix="/execute", tags=["Execute (V3)"])


# ==========================================
# Request/Response Models
# ==========================================


class CodeTestRequest(BaseModel):
    """Request model for testing code execution."""
    code_content: str
    context: Optional[Dict[str, Any]] = None
    executor_type: Literal["auto", "builtin", "subprocess", "remote"] = "auto"
    timeout_seconds: int = 30


class CodeTestResponse(BaseModel):
    """Response model for code test execution."""
    success: bool
    result: Any
    stdout: str
    stderr: str
    execution_time_ms: int
    executor_used: str
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None


class FunctionTestRequest(BaseModel):
    """Request model for testing function execution by ID."""
    context: Optional[Dict[str, Any]] = None
    executor_type: Literal["auto", "builtin", "subprocess", "remote"] = "auto"
    timeout_seconds: int = 30


@router.post("/code/test", response_model=CodeTestResponse, status_code=status.HTTP_200_OK)
def test_code_execution(
    request: CodeTestRequest,
    session: Session = Depends(get_session)
):
    """
    测试运行代码（不保存状态）。用于前端代码编辑器的试运行功能。
    Request: code_content, context (可选), executor_type, timeout_seconds.
    """
    logger.info(f"[V3] Testing code execution, executor_type={request.executor_type}")
    try:
        executor_map = {
            "auto": ExecutorType.AUTO,
            "builtin": ExecutorType.BUILTIN,
            "subprocess": ExecutorType.SUBPROCESS,
            "remote": ExecutorType.REMOTE,
        }
        executor_type = executor_map.get(request.executor_type, ExecutorType.AUTO)
        result = try_function_code(
            code_content=request.code_content,
            context=request.context,
            session=session,
            executor_type=executor_type,
            timeout_seconds=request.timeout_seconds,
        )
        return CodeTestResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_ms=result.execution_time_ms,
            executor_used=result.executor_used,
            error_message=result.error_message,
            error_type=result.error_type,
            traceback=result.traceback,
        )
    except Exception as e:
        logger.error(f"[V3] Code test execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code test execution failed: {str(e)}"
        )


@router.post("/code/validate", status_code=status.HTTP_200_OK)
def validate_code_syntax(request: CodeTestRequest):
    """验证代码语法（不执行）。"""
    is_valid, error_message = validate_syntax(request.code_content)
    return {"valid": is_valid, "error_message": error_message}


@router.post("/function/{function_id}/test", response_model=CodeTestResponse, status_code=status.HTTP_200_OK)
def test_function_execution(
    function_id: str,
    request: FunctionTestRequest,
    session: Session = Depends(get_session)
):
    """测试运行已保存的函数（不保存状态）。"""
    from app.engine.code_executor import execute_function_by_id, ExecutorType

    logger.info(f"[V3] Testing function execution: {function_id}")
    try:
        executor_map = {
            "auto": ExecutorType.AUTO,
            "builtin": ExecutorType.BUILTIN,
            "subprocess": ExecutorType.SUBPROCESS,
            "remote": ExecutorType.REMOTE,
        }
        executor_type = executor_map.get(request.executor_type, ExecutorType.AUTO)
        result = execute_function_by_id(
            session=session,
            function_id=function_id,
            context=request.context or {},
            executor_type=executor_type,
            timeout_seconds=request.timeout_seconds,
        )
        return CodeTestResponse(
            success=result.success,
            result=result.result,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            execution_time_ms=result.execution_time_ms,
            executor_used=result.executor_used or "unknown",
            error_message=result.error_message,
            error_type=result.error_type,
            traceback=result.traceback,
        )
    except Exception as e:
        logger.error(f"[V3] Function test execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function test execution failed: {str(e)}"
        )
