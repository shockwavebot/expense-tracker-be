# test_db_connection.py
import asyncio

import asyncpg


async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres',
            database='expense_tracker',
            host='localhost',
            port=5432
        )
        await conn.close()
        print("Successfully connected to the database!")
        return True
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
