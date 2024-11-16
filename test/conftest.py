# test/conftest.py
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from expense_tracker.core.settings import settings
from expense_tracker.db.session import Base

# Test database URL
TEST_DATABASE_URL = settings.async_database_url.replace(
    settings.POSTGRES_DB,
    f"{settings.POSTGRES_DB}_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.

    The event loop is a global instance that is used to run asynchronous
    operations. Since the tests are run in a single process, a single
    event loop is sufficient. This fixture is used to create the event
    loop before the tests are run, and to close it after the tests are
    finished.

    The reason for using this fixture is that the default behavior of
    pytest-asyncio is to create a new event loop for each test function.
    This can be inefficient, especially if the test functions are
    performing database operations that require a connection to be
    established. By using a single event loop for the entire test
    session, we can avoid this overhead.

    Note that this fixture is only necessary when using pytest-asyncio
    with the `scope="session"` argument. If the `scope` argument is not
    specified, or if it is set to `"function"`, then the event loop will
    be created and closed for each test function.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine.

    The test database engine is created before the tests are run, and
    dropped after the tests are finished. This is done to ensure that
    the tests are run in a clean database, and to avoid any side effects
    from previous test runs.

    The `scope="session"` argument is used to ensure that the test
    database engine is only created once, and that it is shared across
    all test functions. This is more efficient than creating and
    dropping the database engine for each test function.

    The `yield` statement is used to pass the test database engine to
    the test functions. The database engine is created before the test
    functions are run, and it is dropped after the test functions are
    finished.

    The `await engine.dispose()` statement is used to close the
    database engine after the tests are finished. This is necessary to
    free up any system resources that were allocated by the database
    engine.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create test database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop test database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    This fixture is used to create a test database session that can be
    used by the test functions. The test database session is created
    before the tests are run, and it is closed after the tests are
    finished.

    The `test_engine` parameter is a fixture that is used to create the
    test database engine. The test database engine is created before
    the tests are run, and it is dropped after the tests are finished.

    The `async_session` object is created using the `sessionmaker`
    function from the `sqlalchemy.ext.asyncio` module. The
    `sessionmaker` function takes the test database engine as an
    argument, and it returns a session class that can be used to create
    a test database session.

    The `async with` statement is used to create a test database session
    using the `async_session` class. The `async with` statement ensures
    that the test database session is closed after the tests are
    finished, regardless of whether an exception is raised or not.

    The `yield` statement is used to pass the test database session to
    the test functions. The test database session is created before the
    test functions are run, and it is closed after the test functions are
    finished.

    The `await session.rollback()` statement is used to rollback any
    changes that were made to the test database session. This is done to
    ensure that the test database session is left in a clean state
    after the tests are finished.
    """
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing.

    This fixture creates an instance of the `AsyncClient` class from the
    `httpx` library. The `AsyncClient` class is a context manager that
    provides a convenient way to send HTTP requests and receive
    responses.

    The `base_url` parameter is set to `http://localhost:8000`, which is
    the default URL for the FastAPI application.

    The `timeout` parameter is set to 30 seconds, which is a reasonable
    value for most test cases.

    The `yield` statement is used to pass the `AsyncClient` instance to
    the test functions. The `AsyncClient` instance is created before the
    test functions are run, and it is closed after the test functions are
    finished.

    The `async with` statement is used to ensure that the `AsyncClient`
    instance is closed after the test functions are finished, regardless
    of whether an exception is raised or not.
    """
    async with AsyncClient(
        base_url="http://localhost:8000",
        timeout=5.0
    ) as ac:
        yield ac
