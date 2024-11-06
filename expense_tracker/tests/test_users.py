# tests/test_users.py
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from expense_tracker.models.user import User

pytestmark = pytest.mark.asyncio


async def test_create_user(async_client: AsyncClient, db_session):
    response = await async_client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

    # Verify user in database
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one()
    assert user is not None
    assert user.email == "test@example.com"


async def test_create_user_duplicate_email(async_client: AsyncClient):
    # Create first user
    await async_client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser1"
        }
    )

    # Try to create user with same email
    response = await async_client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "password": "password123",
            "username": "testuser2"
        }
    )
    assert response.status_code == 400
