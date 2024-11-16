# expense_tracker/tests/api/test_user_endpoints.py
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
class TestUserEndpoints:
    async def test_create_user(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "api_test_create_user@example.com",
            "username": "api_test_create_user"
        }

        # Act
        response = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data

    async def test_create_user_duplicate_email(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "duplicate_api@example.com",
            "username": "Duplicate API User"
        }

        # Act
        response1 = client.post("/api/v1/users", json=user_data)
        response2 = client.post("/api/v1/users", json=user_data)

        # Assert
        assert response1.status_code == 201
        assert response2.status_code == 409

    async def test_get_user(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "get_api@example.com",
            "username": "Get API User"
        }
        create_response = client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Act
        response = client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]

    async def test_get_nonexistent_user(self, client: TestClient):
        # Act
        response = client.get(
            "/api/v1/users/12345678-1234-5678-1234-567812345678")

        # Assert
        assert response.status_code == 404

    async def test_update_user(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "update_api@example.com",
            "username": "Update API User"
        }
        create_response = client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        update_data = {
            "username": "Updated API Name"
        }

        # Act
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == user_data["email"]

    async def test_delete_user(self, client: TestClient):
        # Arrange
        user_data = {
            "email": "delete_api@example.com",
            "username": "Delete API User"
        }
        create_response = client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Act
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        get_response = client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert delete_response.status_code == 204
        assert get_response.status_code == 404

    async def test_list_users(self, client: TestClient):
        # Arrange
        users_data = [
            {
                "email": f"list_api_{i}@example.com",
                "username": f"List API User {i}"
            }
            for i in range(3)
        ]

        for user_data in users_data:
            client.post("/api/v1/users", json=user_data)

        # Act
        response = client.get("/api/v1/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # May be more due to other tests
        assert all("id" in user for user in data)
