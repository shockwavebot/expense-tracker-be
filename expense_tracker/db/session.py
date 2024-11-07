# expense_tracker/db/session.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from expense_tracker.core.settings import settings

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=True
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
