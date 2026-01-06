"""
FastAPI middleware for request logging and tracing.
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and request ID generation."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Bind request_id to logger context
        context_logger = logger.bind(request_id=request_id)
        
        # Log request start
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        context_logger.info(
            f"Request Start: {request.method} {request.url.path} | Client: {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate process time
            process_time = time.time() - start_time
            
            # Get status code
            status_code = response.status_code
            
            # Log request end
            context_logger.info(
                f"Request End: {request.method} {request.url.path} | "
                f"Status: {status_code} | Process Time: {process_time:.3f}s"
            )
            
            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            context_logger.error(
                f"Request Error: {request.method} {request.url.path} | "
                f"Error: {str(e)} | Process Time: {process_time:.3f}s"
            )
            raise

