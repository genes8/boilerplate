"""Password reset service for handling password recovery."""

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.redis import RedisCache, redis_client

# Password reset token configuration
RESET_TOKEN_LENGTH = 32
RESET_TOKEN_EXPIRE_MINUTES = 30


def generate_reset_token() -> str:
    """
    Generate a secure password reset token.

    Returns:
        str: URL-safe random token.
    """
    return secrets.token_urlsafe(RESET_TOKEN_LENGTH)


def _get_reset_token_key(token: str) -> str:
    """Get Redis key for password reset token."""
    return f"password_reset:{token}"


def _get_user_reset_key(user_id: UUID) -> str:
    """Get Redis key for user's reset token (to prevent multiple tokens)."""
    return f"password_reset_user:{user_id}"


async def create_password_reset_token(user_id: UUID, email: str) -> str:
    """
    Create a password reset token for a user.

    Invalidates any existing reset token for the user.

    Args:
        user_id: User's UUID.
        email: User's email address.

    Returns:
        str: Password reset token.
    """
    cache = RedisCache(redis_client)
    expire_seconds = RESET_TOKEN_EXPIRE_MINUTES * 60

    # Invalidate any existing token for this user
    existing_token = await cache.get(_get_user_reset_key(user_id))
    if existing_token:
        await cache.delete(_get_reset_token_key(existing_token))

    # Generate new token
    token = generate_reset_token()

    # Store token -> user mapping
    token_data = {
        "user_id": str(user_id),
        "email": email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await cache.set_json(_get_reset_token_key(token), token_data, expire=expire_seconds)

    # Store user -> token mapping (for invalidation)
    await cache.set(_get_user_reset_key(user_id), token, expire=expire_seconds)

    return token


async def verify_password_reset_token(token: str) -> dict | None:
    """
    Verify a password reset token and return associated data.

    Args:
        token: Password reset token.

    Returns:
        dict: Token data (user_id, email) if valid, None otherwise.
    """
    cache = RedisCache(redis_client)
    token_data = await cache.get_json(_get_reset_token_key(token))

    if token_data is None:
        return None

    return token_data


async def invalidate_password_reset_token(token: str, user_id: UUID) -> bool:
    """
    Invalidate a password reset token after use.

    Args:
        token: Password reset token.
        user_id: User's UUID.

    Returns:
        bool: True if invalidated successfully.
    """
    cache = RedisCache(redis_client)

    # Delete both keys
    await cache.delete(_get_reset_token_key(token))
    await cache.delete(_get_user_reset_key(user_id))

    return True


async def get_reset_token_ttl(token: str) -> int:
    """
    Get remaining time-to-live for a reset token.

    Args:
        token: Password reset token.

    Returns:
        int: TTL in seconds, -1 if token doesn't exist.
    """
    cache = RedisCache(redis_client)
    return await cache.ttl(_get_reset_token_key(token))
