"""
MDP Sandbox Service - Isolated Code Execution Environment

This service provides a secure, isolated environment for executing
user-defined Python functions. It runs as a separate microservice
in Kubernetes for better security and resource isolation.

Features:
- Process isolation via subprocess
- Timeout control
- Resource limits (via K8s)
- Non-root execution
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import subprocess
import json
import time
import os
import sys

app = FastAPI(
    title="MDP Sandbox",
    description="Isolated code execution service for MDP Platform",
    version="1.0.0"
)


# ==========================================
# Request/Response Models
# ==========================================

class CodeExecuteRequest(BaseModel):
    """Request model for code execution."""
    code_content: str = Field(..., description="Python code to execute")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Execution context")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")


class CodeExecuteResponse(BaseModel):
    """Response model for code execution."""
    success: bool
    result: Any = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: int = 0
    executor_used: str = "sandbox"
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    python_version: str


# ==========================================
# Code Wrapper Template
# ==========================================

WRAPPER_TEMPLATE = '''
import sys
import json
import traceback
import io
from contextlib import redirect_stdout, redirect_stderr

# Read context from stdin
context = json.loads(sys.stdin.read())

# Capture stdout and stderr
stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

try:
    # User code (will be indented and inserted here)
{user_code}
    
    # Check if main function exists
    if 'main' not in dir():
        raise ValueError("Code must define a 'main(context)' function")
    
    # Execute main function with output capture
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        result = main(context)
    
    # Ensure result is JSON serializable
    try:
        json.dumps(result)
        serializable_result = result
    except (TypeError, ValueError):
        serializable_result = str(result)
    
    output = {{
        "success": True,
        "result": serializable_result,
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue()
    }}
    print(json.dumps(output))
    
except Exception as e:
    output = {{
        "success": False,
        "result": None,
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue(),
        "error_message": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(output))
'''


# ==========================================
# Helper Functions
# ==========================================

def indent_code(code: str, spaces: int = 4) -> str:
    """Add indentation to code lines."""
    lines = code.split('\n')
    indented_lines = [' ' * spaces + line if line.strip() else line for line in lines]
    return '\n'.join(indented_lines)


def get_python_executable() -> str:
    """Get the Python interpreter path."""
    return sys.executable


# ==========================================
# API Endpoints
# ==========================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint for K8s probes."""
    return HealthResponse(
        status="healthy",
        service="mdp-sandbox",
        version="1.0.0",
        python_version=sys.version.split()[0]
    )


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "MDP Sandbox Service", "version": "1.0.0"}


@app.post("/execute", response_model=CodeExecuteResponse)
def execute_code(request: CodeExecuteRequest):
    """
    Execute Python code in an isolated subprocess.
    
    The code must define a `main(context)` function that will be called
    with the provided context dictionary.
    
    Example code:
    ```python
    def main(context):
        x = context.get('x', 0)
        return x * 2
    ```
    """
    start_time = time.time()
    
    # Prepare the wrapper code
    indented_code = indent_code(request.code_content)
    wrapper_code = WRAPPER_TEMPLATE.format(user_code=indented_code)
    
    try:
        # Serialize context to JSON
        context_json = json.dumps(request.context or {}, ensure_ascii=False, default=str)
        
        # Get Python executable
        python_path = get_python_executable()
        
        # Execute in subprocess
        proc = subprocess.run(
            [python_path, '-c', wrapper_code],
            input=context_json,
            capture_output=True,
            text=True,
            timeout=request.timeout_seconds,
            cwd=os.getcwd(),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Parse output
        stdout_content = proc.stdout
        stderr_content = proc.stderr
        
        if proc.returncode == 0 and stdout_content.strip():
            try:
                # Parse JSON output (last line)
                output = json.loads(stdout_content.strip().split('\n')[-1])
                
                return CodeExecuteResponse(
                    success=output.get("success", False),
                    result=output.get("result"),
                    stdout=output.get("stdout", ""),
                    stderr=output.get("stderr", "") + stderr_content,
                    execution_time_ms=execution_time_ms,
                    executor_used="sandbox",
                    error_message=output.get("error_message"),
                    error_type=output.get("error_type"),
                    traceback=output.get("traceback")
                )
            except json.JSONDecodeError:
                return CodeExecuteResponse(
                    success=False,
                    stdout=stdout_content,
                    stderr=stderr_content,
                    execution_time_ms=execution_time_ms,
                    executor_used="sandbox",
                    error_message="Failed to parse execution output as JSON",
                    error_type="JSONDecodeError"
                )
        else:
            # Process failed
            return CodeExecuteResponse(
                success=False,
                stdout=stdout_content,
                stderr=stderr_content,
                execution_time_ms=execution_time_ms,
                executor_used="sandbox",
                error_message=stderr_content or f"Process exited with code {proc.returncode}",
                error_type="SubprocessError"
            )
            
    except subprocess.TimeoutExpired:
        execution_time_ms = int((time.time() - start_time) * 1000)
        return CodeExecuteResponse(
            success=False,
            execution_time_ms=execution_time_ms,
            executor_used="sandbox",
            error_message=f"Execution timed out after {request.timeout_seconds} seconds",
            error_type="TimeoutError"
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        return CodeExecuteResponse(
            success=False,
            stderr=str(e),
            execution_time_ms=execution_time_ms,
            executor_used="sandbox",
            error_message=str(e),
            error_type=type(e).__name__
        )


@app.post("/validate")
def validate_code(request: CodeExecuteRequest):
    """
    Validate Python code syntax without executing.
    """
    try:
        compile(request.code_content, '<string>', 'exec')
        return {"valid": True, "error_message": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error_message": f"Syntax error at line {e.lineno}: {e.msg}"
        }


# ==========================================
# Main Entry Point
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
