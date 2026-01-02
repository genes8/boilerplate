"""Unit tests for JWT token service."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.services.jwt import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    create_tokens,
    decode_token,
    is_token_expired,
)


class TestJWTTokenCreation:
    """Tests for JWT token creation functions."""

    def test_create_access_token_returns_string(self) -> None:
        """Test that create_access_token returns a string."""
        user_id = uuid4()
        token = create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self) -> None:
        """Test that create_refresh_token returns a string."""
        user_id = uuid4()
        token = create_refresh_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_tokens_returns_tuple(self) -> None:
        """Test that create_tokens returns correct tuple."""
        user_id = uuid4()
        access_token, refresh_token, expires_in = create_tokens(user_id)
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert isinstance(expires_in, int)
        assert expires_in > 0

    def test_access_and_refresh_tokens_are_different(self) -> None:
        """Test that access and refresh tokens are different."""
        user_id = uuid4()
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        assert access_token != refresh_token


class TestJWTTokenDecoding:
    """Tests for JWT token decoding functions."""

    def test_decode_access_token(self) -> None:
        """Test decoding a valid access token."""
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.sub == str(user_id)
        assert payload.type == ACCESS_TOKEN_TYPE

    def test_decode_refresh_token(self) -> None:
        """Test decoding a valid refresh token."""
        user_id = uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.sub == str(user_id)
        assert payload.type == REFRESH_TOKEN_TYPE

    def test_decode_invalid_token(self) -> None:
        """Test decoding an invalid token returns None."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        assert payload is None

    def test_decode_empty_token(self) -> None:
        """Test decoding an empty token returns None."""
        payload = decode_token("")
        assert payload is None

    def test_decode_malformed_token(self) -> None:
        """Test decoding a malformed token returns None."""
        payload = decode_token("not-a-jwt")
        assert payload is None

    def test_token_contains_timestamps(self) -> None:
        """Test that token payload contains exp and iat timestamps."""
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.exp > 0
        assert payload.iat > 0
        assert payload.exp > payload.iat


class TestTokenExpiration:
    """Tests for token expiration checking."""

    def test_fresh_token_not_expired(self) -> None:
        """Test that a freshly created token is not expired."""
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert is_token_expired(payload) is False

    def test_expired_token_detection(self) -> None:
        """Test detection of expired token via payload manipulation."""
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None

        # Manually set expiration to past
        from app.schemas.auth import TokenPayload

        expired_payload = TokenPayload(
            sub=payload.sub,
            exp=int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            iat=payload.iat,
            type=payload.type,
        )

        assert is_token_expired(expired_payload) is True

    def test_token_expiration_boundary(self) -> None:
        """Test token expiration at exact boundary."""
        from app.schemas.auth import TokenPayload

        now = datetime.now(timezone.utc)

        # Token that expires exactly now should be expired
        boundary_payload = TokenPayload(
            sub=str(uuid4()),
            exp=int(now.timestamp()),
            iat=int((now - timedelta(minutes=30)).timestamp()),
            type=ACCESS_TOKEN_TYPE,
        )

        assert is_token_expired(boundary_payload) is True


class TestTokenTypes:
    """Tests for token type differentiation."""

    def test_access_token_has_correct_type(self) -> None:
        """Test that access token has 'access' type."""
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.type == "access"

    def test_refresh_token_has_correct_type(self) -> None:
        """Test that refresh token has 'refresh' type."""
        user_id = uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload is not None
        assert payload.type == "refresh"
