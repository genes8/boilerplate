"""Redis connection and cache management."""

from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import redis.asyncio as redis
from fastapi import Depends

from app.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,  # Maximum number of connections in pool
    retry_on_timeout=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    health_check_interval=30,  # Check connection health every 30 seconds
)


# Redis client
redis_client = redis.Redis(
    connection_pool=redis_pool,
)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Dependency that provides a Redis client.

    Yields:
        redis.Redis: Redis client for the request.

    Example:
        @router.get("/cached-data")
        async def get_cached_data(redis_client: redis.Redis = Depends(get_redis)):
            cached = await redis_client.get("some_key")
            return {"data": cached}
    """
    try:
        yield redis_client
    except Exception:
        # Connection will be returned to pool automatically
        raise


# Type alias for dependency injection
def RedisClient() -> redis.Redis:
    """Redis client dependency."""
    return Depends(get_redis)


async def init_redis() -> None:
    """Initialize Redis connection - test connectivity."""
    try:
        await redis_client.ping()
        print("✅ Redis connection: OK")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connections."""
    await redis_client.close()
    await redis_pool.disconnect()
    print("✅ Redis connections closed")


class RedisCache:
    """High-level cache operations wrapper."""

    def __init__(self, redis_client: redis.Redis):
        self.client = redis_client

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        try:
            return await self.client.get(key)
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: str | int | float | dict[str, Any] | list[Any],
        expire: int | None = None,
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            # Convert non-string values to JSON string
            if not isinstance(value, str):
                import json

                value = json.dumps(value)

            return await self.client.set(key, value, ex=expire)
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(await self.client.delete(key))
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(await self.client.exists(key))
        except Exception:
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for existing key."""
        try:
            return bool(await self.client.expire(key, seconds))
        except Exception:
            return False

    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return await self.client.ttl(key)
        except Exception:
            return -1

    async def increment(self, key: str, amount: int = 1) -> int | None:
        """Increment numeric value."""
        try:
            return await self.client.incrby(key, amount)
        except Exception:
            return None

    async def decrement(self, key: str, amount: int = 1) -> int | None:
        """Decrement numeric value."""
        try:
            return await self.client.decrby(key, amount)
        except Exception:
            return None

    async def get_json(self, key: str) -> Any | None:
        """Get JSON value and deserialize."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None

            import json

            return json.loads(value)
        except Exception:
            return None

    async def set_json(self, key: str, value: Any, expire: int | None = None) -> bool:
        """Set JSON value with serialization."""
        try:
            import json

            json_value = json.dumps(value)
            return await self.client.set(key, json_value, ex=expire)
        except Exception:
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception:
            return 0

    async def get_keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        try:
            return await self.client.keys(pattern)
        except Exception:
            return []


def cache_key(*parts: str, prefix: str = "cache") -> str:
    """
    Generate cache key from parts.

    Args:
        *parts: Parts of the key
        prefix: Key prefix (default: "cache")

    Returns:
        str: Generated cache key

    Example:
        cache_key("user", "123", "profile") -> "cache:user:123:profile"
    """
    return ":".join([prefix, *parts])


def session_cache_key(session_id: str, key: str) -> str:
    """Generate session-specific cache key."""
    return cache_key("session", session_id, key)


def user_cache_key(user_id: str, key: str) -> str:
    """Generate user-specific cache key."""
    return cache_key("user", user_id, key)


def generate_session_id() -> str:
    """Generate unique session ID."""
    return str(uuid4())
