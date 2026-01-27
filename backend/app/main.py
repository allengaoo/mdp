"""
FastAPI application entry point.
"""
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.api.v1 import ontology, execute
from app.api.v3 import router as v3_router
from app.core.middleware import LoggingMiddleware
from app.core.logger import logger
from app.core.config import settings

app = FastAPI(
    title="MDP Platform API",
    version="3.1.0",
    description="""
    MDP Platform API - Ontology Management and Runtime Execution System.
    
    ## Features
    
    * **Meta Layer**: Manage Object Types, Link Types, Functions, and Actions
    * **Instance Layer**: Create and query object instances
    * **Runtime Layer**: Execute actions and functions
    * **Search Layer**: Hybrid search with text and vector
    
    ## API Documentation
    
    * **Swagger UI**: Interactive API documentation (this page)
    * **ReDoc**: Alternative documentation format at `/redoc`
    * **OpenAPI Schema**: JSON schema at `/openapi.json`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware (allow all origins for demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware (must be before routers)
app.add_middleware(LoggingMiddleware)

# Mount static files
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Register API routers
app.include_router(ontology.router, prefix="/api/v1/meta", tags=["Meta"])
app.include_router(execute.router, prefix="/api/v1")
app.include_router(v3_router, prefix="/api/v3")


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.exception(exc)
    
    if settings.DEBUG:
        traceback_str = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Server Error",
                "error_msg": str(exc),
                "traceback": traceback_str,
                "error_type": type(exc).__name__,
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "MDP Platform Demo API V3.1"}
