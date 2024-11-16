# tests/test_users.py
import uuid
from typing import Dict

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def rnd_email() -> str:
    rnd = str(uuid.uuid4())[:8]
    return f"test{rnd}@example.com"


async def create_test_user(client: AsyncClient, email: str = "test@example.com", name: str = "Test User") -> Dict:
    """Helper function to create a test user."""
    response = await client.post(
        "/api/v1/users",
        json={"email": email, "username": name}
    )
    return response.json()


class TestUserEndpoints:
    async def test_create_user(self, client: AsyncClient) -> None:
        """Test user creation endpoint."""
        email = rnd_email()
        response = await client.post(
            "/api/v1/users",
            json={
                "email": email,
                "username": "Test User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == email
        assert data["username"] == "Test User"
        assert "id" in data

        # Test duplicate email
        response = await client.post(
            "/api/v1/users",
            json={
                "email": email,
                "username": "Another User"
            }
        )
        assert response.status_code == 409

    async def test_get_user(self, client: AsyncClient) -> None:
        """Test get user endpoint."""
        email = rnd_email()
        user = await create_test_user(client, email)
        user_id = user["id"]

        # Test successful retrieval
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["id"] == user_id

        # Test non-existent user
        response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_update_user(self, client: AsyncClient) -> None:
        """Test update user endpoint."""
        # Create a test user first
        email = rnd_email()
        user = await create_test_user(client, email)
        user_id = user["id"]

        # Test successful update
        response = await client.put(
            f"/api/v1/users/{user_id}",
            json={
                "username": "Updated Name"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "Updated Name"
        assert data["email"] == email

        # Test update with duplicate email
        other_user = await create_test_user(client, f"other_{email}")
        other_user_id = other_user["id"]
        response = await client.put(
            f"/api/v1/users/{other_user_id}",
            json={
                "email": email
            }
        )
        assert response.status_code == 409

    async def test_delete_user(self, client: AsyncClient) -> None:
        """Test delete user endpoint."""
        # Create a test user first
        user = await create_test_user(client, "delete@example.com")
        user_id = user["id"]

        # Test successful deletion
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify user is deleted
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404

        # Test deleting non-existent user
        response = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_list_users(self, client: AsyncClient) -> None:
        # Test listing users
        response = await client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        # Test pagination
        response = await client.get("/api/v1/users?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2
