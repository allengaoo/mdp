"""
Database connection and session management.
MDP Platform V3.1 - Metadata-Driven Architecture
"""
from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

# Synchronous engine for standard operations
engine = create_engine(settings.database_url, echo=settings.DEBUG)

# Async engine for SQL runner (read-only queries)
# Convert mysql:// to mysql+aiomysql:// for async support
_async_url = settings.database_url
if _async_url.startswith("mysql://"):
    _async_url = _async_url.replace("mysql://", "mysql+aiomysql://", 1)
elif _async_url.startswith("mysql+pymysql://"):
    _async_url = _async_url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
elif _async_url.startswith("sqlite://"):
    _async_url = _async_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

instance_engine = create_async_engine(_async_url, echo=settings.DEBUG)


def get_session():
    """Dependency for getting database session (FastAPI)."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Context manager for getting database session (background tasks)."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)

