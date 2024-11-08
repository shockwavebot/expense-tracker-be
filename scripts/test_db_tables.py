import asyncio
import logging
import os

import asyncpg

from expense_tracker.core.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))

EXPECTED_TABLES = ['user', 'category', 'expense',
                   'shared_expense', 'alembic_version']


async def verify_tables():
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB
    )

    try:
        # Get all table names
        result = await conn.fetch('SELECT tablename FROM pg_tables WHERE schemaname = \'public\'')
        tables = [row['tablename'] for row in result]
        logger.info(f"Existing tables: {tables}")
        # Check if all expected tables are present
        for table in EXPECTED_TABLES:
            if table not in tables:
                print(f"Table {table} not found! ❌")
            else:
                print(f"Table {table} found! ✅")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(verify_tables())
