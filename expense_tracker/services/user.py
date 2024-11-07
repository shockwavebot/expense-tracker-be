# expense_tracker/services/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.security import get_password_hash, verify_password
from expense_tracker.models.user import User
from expense_tracker.schemas.user import UserCreate, UserUpdate
from expense_tracker.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(self.model).filter(self.model.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        query = select(self.model).filter(self.model.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User | None:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        return user.is_active
