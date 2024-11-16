# expense_tracker/tests/services/test_user_service.py
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.exceptions import DuplicateEmailError, UserNotFoundError
from expense_tracker.schemas.user import UserCreate, UserUpdate
from expense_tracker.services.user import UserService


def rnd_email() -> str:
    rnd = str(uuid.uuid4())[:16]
    return f"test_{rnd}@example.com"


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user(self, db_session: AsyncSession):
        # Arrange
        email = rnd_email()
        service = UserService(db_session)
        user_data = UserCreate(
            email=email,
            username="Test User"
        )

        # Act
        user = await service.create_user(user_data)

        # Assert
        assert user.email == user_data.email
        assert user.username == user_data.username
        assert user.id is not None

    async def test_create_duplicate_email(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email=rnd_email(),
            username="Test User"
        )

        # Act & Assert
        await service.create_user(user_data)
        with pytest.raises(DuplicateEmailError):
            await service.create_user(user_data)

    async def test_get_user_by_id(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email=rnd_email(),
            username="Get User"
        )
        created_user = await service.create_user(user_data)

        # Act
        user = await service.get_user_by_id(str(created_user.id))

        # Assert
        assert user.id == created_user.id
        assert user.email == user_data.email
        assert user.username == user_data.username

    async def test_get_nonexistent_user(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await service.get_user_by_id("12345678-1234-5678-1234-567812345678")

    async def test_update_user(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email=rnd_email(),
            username="Update User"
        )
        user = await service.create_user(user_data)

        update_data = UserUpdate(username="Updated Name")

        # Act
        updated_user = await service.update_user(str(user.id), update_data)

        # Assert
        assert updated_user.id == user.id
        assert updated_user.username == "Updated Name"
        assert updated_user.email == user_data.email

    async def test_delete_user(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email=rnd_email(),
            username="Delete User"
        )
        user = await service.create_user(user_data)

        # Act
        await service.delete_user(str(user.id))

        # Assert
        with pytest.raises(UserNotFoundError):
            await service.get_user_by_id(str(user.id))

    async def test_list_users(self, db_session: AsyncSession):
        # Arrange
        test_email = rnd_email()
        service = UserService(db_session)
        users_data = [
            UserCreate(email=f"user{i}{test_email}", username=f"User {i}")
            for i in range(3)
        ]

        for user_data in users_data:
            await service.create_user(user_data)

        # Act
        users = await service.list_users(skip=0, limit=10)

        # Assert
        assert len(users) >= 3  # May be more due to other tests
        assert all(user.id is not None for user in users)
