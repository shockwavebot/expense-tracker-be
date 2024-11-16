# expense_tracker/tests/services/test_user_service.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from expense_tracker.core.exceptions import DuplicateEmailError, UserNotFoundError
from expense_tracker.schemas.user import UserCreate, UserUpdate
from expense_tracker.services.user import UserService


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            name="Test User"
        )

        # Act
        user = await service.create_user(user_data)

        # Assert
        assert user.email == user_data.email
        assert user.name == user_data.name
        assert user.id is not None

    async def test_create_duplicate_email(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email="duplicate@example.com",
            name="Test User"
        )

        # Act & Assert
        await service.create_user(user_data)
        with pytest.raises(DuplicateEmailError):
            await service.create_user(user_data)

    async def test_get_user_by_id(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email="get@example.com",
            name="Get User"
        )
        created_user = await service.create_user(user_data)

        # Act
        user = await service.get_user_by_id(str(created_user.id))

        # Assert
        assert user.id == created_user.id
        assert user.email == user_data.email
        assert user.name == user_data.name

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
            email="update@example.com",
            name="Update User"
        )
        user = await service.create_user(user_data)

        update_data = UserUpdate(name="Updated Name")

        # Act
        updated_user = await service.update_user(str(user.id), update_data)

        # Assert
        assert updated_user.id == user.id
        assert updated_user.name == "Updated Name"
        assert updated_user.email == user_data.email

    async def test_delete_user(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        user_data = UserCreate(
            email="delete@example.com",
            name="Delete User"
        )
        user = await service.create_user(user_data)

        # Act
        await service.delete_user(str(user.id))

        # Assert
        with pytest.raises(UserNotFoundError):
            await service.get_user_by_id(str(user.id))

    async def test_list_users(self, db_session: AsyncSession):
        # Arrange
        service = UserService(db_session)
        users_data = [
            UserCreate(email=f"user{i}@example.com", name=f"User {i}")
            for i in range(3)
        ]

        for user_data in users_data:
            await service.create_user(user_data)

        # Act
        users = await service.list_users(skip=0, limit=10)

        # Assert
        assert len(users) >= 3  # May be more due to other tests
        assert all(user.id is not None for user in users)
