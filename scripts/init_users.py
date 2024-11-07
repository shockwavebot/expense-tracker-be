# scripts/init_db.py
import asyncio
import logging

from sqlalchemy import text

from alembic import command
from alembic.config import Config
from expense_tracker.core.security import get_password_hash
from expense_tracker.db.session import AsyncSessionLocal, engine
from expense_tracker.models import Base
from expense_tracker.models.category import Category
from expense_tracker.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_data() -> None:
    """Create initial users and categories"""
    try:
        async with AsyncSessionLocal() as session:
            # Create test users
            test_users = [
                User(
                    email="john@example.com",
                    username="johndoe",
                    hashed_password=get_password_hash("password123"),
                    is_active=True
                ),
                User(
                    email="jane@example.com",
                    username="janedoe",
                    hashed_password=get_password_hash("password123"),
                    is_active=True
                )
            ]

            for user in test_users:
                session.add(user)
            await session.commit()

            # Refresh to get their IDs
            for user in test_users:
                await session.refresh(user)

            # Create default categories for each user
            default_categories = [
                "Groceries",
                "Transportation",
                "Entertainment",
                "Utilities",
                "Healthcare",
                "Shopping",
                "Restaurants",
                "Travel"
            ]

            for user in test_users:
                categories = [
                    Category(
                        name=cat_name,
                        description=f"Expenses related to {cat_name.lower()}",
                        user_id=user.id
                    )
                    for cat_name in default_categories
                ]
                for category in categories:
                    session.add(category)

            await session.commit()
            logger.info("Initial data created successfully")

            # Log created users
            result = await session.execute(
                text("SELECT id, email, username FROM users")
            )
            users = result.fetchall()
            logger.info("Created users:")
            for user in users:
                logger.info(f"ID: {user[0]}, Email: {
                            user[1]}, Username: {user[2]}")

            # Log created categories
            result = await session.execute(
                text("SELECT id, name, user_id FROM categories")
            )
            categories = result.fetchall()
            logger.info("Created categories:")
            for category in categories:
                logger.info(f"ID: {category[0]}, Name: {
                            category[1]}, User ID: {category[2]}")

    except Exception as e:
        logger.error(f"Error creating initial data: {str(e)}")
        raise


async def init_db() -> None:
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully")

        # Create initial data
        await create_initial_data()

        # Run Alembic migrations
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
        logger.info("Alembic migrations stamped")

        # Verify database connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await result.fetchone()
            logger.info("Database connection verified")

        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


async def verify_tables() -> None:
    try:
        async with engine.connect() as conn:
            # Get all table names
            result = await conn.execute(
                text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
            )
            tables = [row[0] for row in await result.fetchall()]
            logger.info(f"Existing tables: {tables}")

            # Get row counts for each table
            for table in tables:
                result = await conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                count = await result.scalar()
                logger.info(f"Table {table} has {count} rows")

    except Exception as e:
        logger.error(f"Error verifying tables: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(verify_tables())
