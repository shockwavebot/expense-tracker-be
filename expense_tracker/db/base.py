# expense_tracker/db/base.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from expense_tracker.core.config import settings

# Convert the PostgreSQL URL to AsyncPG URL
db_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(db_url, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
