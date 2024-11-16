# expense_tracker/tests/test_db_connection.py
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test that we can connect to the test database."""
    try:
        result = await db_session.execute(text('SELECT 1'))
        value = result.scalar()
        assert value == 1
        print(f"Successfully connected to database and got value: {value}")
    except Exception as e:
        print(f"Database connection failed with error: {str(e)}")
        raise
