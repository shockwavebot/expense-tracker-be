# expense_tracker/services/user.py
import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.exceptions import DuplicateEmailError, UserNotFoundError
from expense_tracker.models.user import User
from expense_tracker.schemas.user import UserCreate, UserUpdate

current_time = datetime.datetime.now()


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            email=user_data.email,
            username=user_data.username,
            created_at=current_time,
            updated_at=current_time
        )

        try:
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            return user
        except IntegrityError as e:
            await self.db_session.rollback()
            if "duplicate key" in str(e):
                raise DuplicateEmailError(
                    f"Email {user_data.email} already exists")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """Update a user"""
        user = await self.get_user_by_id(user_id)

        # Update only provided fields
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.username is not None:
            user.username = user_data.username

        try:
            await self.db_session.commit()
            await self.db_session.refresh(user)
            return user
        except IntegrityError as e:
            await self.db_session.rollback()
            if "duplicate key" in str(e):
                raise DuplicateEmailError(
                    f"Email {user_data.email} already exists")
            raise

    async def delete_user(self, user_id: str) -> None:
        """Delete a user"""
        user = await self.get_user_by_id(user_id)
        await self.db_session.delete(user)
        await self.db_session.commit()

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination"""
        query = select(User).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
