# expense_tracker/tests/test_auth.py
import pytest
from httpx import AsyncClient

from expense_tracker.main import app


@pytest.mark.asyncio
async def test_auth_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Register a new user
        register_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }

        response = await client.post(
            "/api/v1/auth/register",
            json=register_data
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == register_data["email"]
        assert user_data["username"] == register_data["username"]

        # 2. Try to login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }

        response = await client.post(
            "/api/v1/auth/login",
            json=login_data
        )
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # 3. Test with invalid credentials
        invalid_login = {
            "email": register_data["email"],
            "password": "wrongpassword"
        }

        response = await client.post(
            "/api/v1/auth/login",
            json=invalid_login
        )
        assert response.status_code == 401

# Save this as test_manual.py for manual testing
test_data = {
    "register": {
        "url": "http://localhost:8000/api/v1/auth/register",
        "data": {
            "email": "user@example.com",
            "username": "testuser",
            "password": "password123"
        }
    },
    "login": {
        "url": "http://localhost:8000/api/v1/auth/login",
        "data": {
            "email": "user@example.com",
            "password": "password123"
        }
    }
}


async def manual_test():
    async with AsyncClient() as client:
        # Register
        print("\nTesting Registration:")
        response = await client.post(
            test_data["register"]["url"],
            json=test_data["register"]["data"]
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Login
        print("\nTesting Login:")
        response = await client.post(
            test_data["login"]["url"],
            json=test_data["login"]["data"]
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(manual_test())
