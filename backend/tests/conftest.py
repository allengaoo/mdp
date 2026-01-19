"""
Pytest configuration and fixtures for API testing.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.db import engine, get_session


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"


@pytest.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def db_session():
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session
