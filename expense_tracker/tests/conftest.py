# expense_tracker/tests/conftest.py
from typing import AsyncGenerator

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from expense_tracker.core.settings import Settings
from expense_tracker.db.session import Base, get_session
from expense_tracker.main import app

# Create test settings
test_settings = Settings(
    POSTGRES_DB="expense_tracker_test",
)


@pytest_asyncio.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        test_settings.async_database_url,
        poolclass=NullPool,
        echo=True
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    session = AsyncSession(test_engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """Create a test client with a test database session."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.rollback()
            await db_session.close()

    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
