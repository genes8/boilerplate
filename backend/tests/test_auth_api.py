"""Integration tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test registration with duplicate email fails."""
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration with same email
        duplicate_data = {
            **test_user_data,
            "username": "different_username",
        }
        response = await client.post("/api/v1/auth/register", json=duplicate_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test registration with duplicate username fails."""
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration with same username
        duplicate_data = {
            **test_user_data,
            "email": "different@example.com",
        }
        response = await client.post("/api/v1/auth/register", json=duplicate_data)

        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient) -> None:
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_username(self, client: AsyncClient) -> None:
        """Test registration with invalid username fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "invalid username!",  # Contains space and special char
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test successful login."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test login with wrong password fails."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        """Test login with nonexistent user fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestMeEndpoint:
    """Tests for GET /api/v1/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_me_authenticated(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test getting current user info when authenticated."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        access_token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client: AsyncClient) -> None:
        """Test getting current user info without authentication fails."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client: AsyncClient) -> None:
        """Test getting current user info with invalid token fails."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_success(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test successful token refresh."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient) -> None:
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test successful logout."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        access_token = login_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, client: AsyncClient) -> None:
        """Test logout without authentication fails."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Tests for POST /api/v1/auth/change-password endpoint."""

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test successful password change."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        access_token = login_response.json()["access_token"]

        # Change password
        new_password = "NewPassword456!"
        response = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": test_user_data["password"],
                "new_password": new_password,
            },
        )

        assert response.status_code == 200

        # Verify can login with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test password change with wrong current password fails."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        access_token = login_response.json()["access_token"]

        # Try to change password with wrong current password
        response = await client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword456!",
            },
        )

        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]


class TestPasswordResetEndpoints:
    """Tests for password reset endpoints."""

    @pytest.mark.asyncio
    async def test_password_reset_request(
        self, client: AsyncClient, test_user_data: dict[str, str]
    ) -> None:
        """Test password reset request."""
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Request password reset
        response = await client.post(
            "/api/v1/auth/password/reset",
            json={"email": test_user_data["email"]},
        )

        assert response.status_code == 200
        # Should always return success for security
        assert "password reset link" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_nonexistent_email(
        self, client: AsyncClient
    ) -> None:
        """Test password reset with nonexistent email still returns success."""
        response = await client.post(
            "/api/v1/auth/password/reset",
            json={"email": "nonexistent@example.com"},
        )

        # Should still return success for security (no email enumeration)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_password_reset_confirm_invalid_token(
        self, client: AsyncClient
    ) -> None:
        """Test password reset confirm with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/password/reset/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword123!",
            },
        )

        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]
