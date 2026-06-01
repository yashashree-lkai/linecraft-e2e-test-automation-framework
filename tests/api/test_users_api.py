"""
tests/api/test_users_api.py — Example API tests for a /users endpoint.
No browser required — uses ApiClient fixture directly.
"""

import pytest
from utils.helpers import random_email, random_string


@pytest.mark.api
class TestUsersApi:
    """CRUD operations on the /users resource."""

    def test_get_current_user_returns_200(self, api_client):
        """GET /users/me → 200 with expected fields."""
        resp = api_client.get("/users/me")
        api_client.assert_status(resp, 200)
        api_client.assert_schema(resp, required_fields=["id", "email", "name"])

    def test_create_user_returns_201(self, api_client):
        """POST /users → 201 with the created user's id."""
        payload = {
            "name": random_string(6, prefix="User_"),
            "email": random_email(),
            "password": "TestPass123!",
        }
        resp = api_client.post("/users", json=payload)
        api_client.assert_status(resp, 201)
        data = resp.json()
        assert "id" in data, "Created user response must contain 'id'."

    def test_create_user_with_duplicate_email_returns_409(self, api_client):
        """POST /users with existing email → 409 Conflict."""
        email = random_email()
        api_client.post("/users", json={"name": "A", "email": email, "password": "Pass1!"})
        resp = api_client.post("/users", json={"name": "B", "email": email, "password": "Pass2!"})
        api_client.assert_status(resp, 409)

    def test_update_user_name(self, api_client):
        """PATCH /users/:id → 200 with updated name."""
        # Create
        create_resp = api_client.post("/users", json={
            "name": "Original Name",
            "email": random_email(),
            "password": "Pass123!",
        })
        user_id = create_resp.json()["id"]

        # Update
        resp = api_client.patch(f"/users/{user_id}", json={"name": "Updated Name"})
        api_client.assert_status(resp, 200)
        api_client.assert_field(resp, "name", "Updated Name")

    def test_delete_user(self, api_client):
        """DELETE /users/:id → 204 No Content."""
        create_resp = api_client.post("/users", json={
            "name": "To Delete",
            "email": random_email(),
            "password": "Pass123!",
        })
        user_id = create_resp.json()["id"]

        resp = api_client.delete(f"/users/{user_id}")
        api_client.assert_status(resp, 204)

    def test_get_nonexistent_user_returns_404(self, api_client):
        """GET /users/00000 → 404 Not Found."""
        resp = api_client.get("/users/nonexistent-id-00000")
        api_client.assert_status(resp, 404)


@pytest.mark.api
class TestAuthApi:
    """Authentication endpoint tests."""

    def test_login_with_valid_credentials(self, api_client):
        """POST /auth/login → 200 with access_token."""
        # Use a pre-existing test account
        import os
        resp = api_client.post("/auth/login", json={
            "email": os.getenv("TEST_USERNAME", "test@example.com"),
            "password": os.getenv("TEST_PASSWORD", "TestPassword123!"),
        })
        api_client.assert_status(resp, 200)
        data = resp.json()
        assert "access_token" in data or "token" in data, \
            "Response must contain a token field."

    def test_login_with_wrong_password(self, api_client):
        """POST /auth/login with bad password → 401."""
        resp = api_client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "definitely-wrong-password",
        })
        api_client.assert_status(resp, 401)

    def test_protected_route_without_token(self):
        """GET /users/me without Authorization header → 401."""
        import requests, os
        resp = requests.get(
            os.getenv("API_BASE_URL", "https://api.your-app.com") + "/users/me"
        )
        assert resp.status_code == 401, \
            f"Expected 401, got {resp.status_code}"
