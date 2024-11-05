# scripts/init_db.py
import asyncio

import asyncpg

from expense_tracker.core.config import settings


async def init_db():
    # Connect to default database first
    sys_conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database='postgres'
    )

    try:
        # Check if our database exists
        exists = await sys_conn.fetchval(
            'SELECT 1 FROM pg_database WHERE datname = $1',
            settings.POSTGRES_DB
        )

        if not exists:
            print(f"Creating database {settings.POSTGRES_DB}")
            # Create database if it doesn't exist
            await sys_conn.execute(
                f'CREATE DATABASE {settings.POSTGRES_DB}'
            )
            print("Database created successfully!")
        else:
            print(f"Database {settings.POSTGRES_DB} already exists")

    finally:
        await sys_conn.close()

    print("Checking connection to the new database...")
    try:
        # Test connection to the new database
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )
        await conn.close()
        print("Successfully connected to the new database!")
    except Exception as e:
        print(f"Error connecting to the new database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
