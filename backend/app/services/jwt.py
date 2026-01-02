"""JWT token service for authentication."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.config import settings
from app.core.redis import RedisCache, redis_client, user_cache_key
from app.schemas.auth import TokenPayload

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_access_token(user_id: UUID) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User's UUID.

    Returns:
        str: Encoded JWT access token.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": ACCESS_TOKEN_TYPE,
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a JWT refresh token for a user.

    Args:
        user_id: User's UUID.

    Returns:
        str: Encoded JWT refresh token.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": REFRESH_TOKEN_TYPE,
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload | None:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string.

    Returns:
        TokenPayload: Decoded token payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            exp=payload["exp"],
            iat=payload["iat"],
            type=payload["type"],
        )
    except JWTError:
        return None


def is_token_expired(token_payload: TokenPayload) -> bool:
    """
    Check if a token has expired.

    Args:
        token_payload: Decoded token payload.

    Returns:
        bool: True if token is expired, False otherwise.
    """
    now = datetime.now(timezone.utc)
    exp = datetime.fromtimestamp(token_payload.exp, tz=timezone.utc)
    return now >= exp


async def store_refresh_token(user_id: UUID, refresh_token: str) -> bool:
    """
    Store refresh token in Redis for validation.

    Args:
        user_id: User's UUID.
        refresh_token: Refresh token to store.

    Returns:
        bool: True if stored successfully, False otherwise.
    """
    cache = RedisCache(redis_client)
    key = user_cache_key(str(user_id), "refresh_token")
    expire_seconds = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    return await cache.set(key, refresh_token, expire=expire_seconds)


async def get_stored_refresh_token(user_id: UUID) -> str | None:
    """
    Get stored refresh token from Redis.

    Args:
        user_id: User's UUID.

    Returns:
        str: Stored refresh token if exists, None otherwise.
    """
    cache = RedisCache(redis_client)
    key = user_cache_key(str(user_id), "refresh_token")
    return await cache.get(key)


async def invalidate_refresh_token(user_id: UUID) -> bool:
    """
    Invalidate (delete) a user's refresh token from Redis.

    Args:
        user_id: User's UUID.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    cache = RedisCache(redis_client)
    key = user_cache_key(str(user_id), "refresh_token")
    return await cache.delete(key)


async def validate_refresh_token(user_id: UUID, refresh_token: str) -> bool:
    """
    Validate a refresh token against the stored token.

    Args:
        user_id: User's UUID.
        refresh_token: Refresh token to validate.

    Returns:
        bool: True if token is valid and matches stored token, False otherwise.
    """
    stored_token = await get_stored_refresh_token(user_id)
    if stored_token is None:
        return False
    return stored_token == refresh_token


def create_tokens(user_id: UUID) -> tuple[str, str, int]:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id: User's UUID.

    Returns:
        tuple: (access_token, refresh_token, expires_in_seconds)
    """
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return access_token, refresh_token, expires_in
