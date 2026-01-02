"""Redis test endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.core.redis import RedisCache, cache_key, generate_session_id, get_redis

router = APIRouter(prefix="/test/redis", tags=["redis-test"])


@router.get("/ping")
async def redis_ping(redis_client: Redis = Depends(get_redis)) -> dict[str, str]:
    """Test Redis connection."""
    await redis_client.ping()
    return {"status": "Redis connection OK"}


@router.get("/cache/{key}")
async def get_cache_value(
    key: str, redis_client: Redis = Depends(get_redis)
) -> dict[str, Any]:
    """Get value from cache."""
    cache = RedisCache(redis_client)
    value = await cache.get(key)
    return {"key": key, "value": value, "found": value is not None}


@router.post("/cache/{key}")
async def set_cache_value(
    key: str,
    value: str,
    redis_client: Redis = Depends(get_redis),
    expire: int | None = None,
) -> dict[str, Any]:
    """Set value in cache."""
    cache = RedisCache(redis_client)
    success = await cache.set(key, value, expire)
    return {"key": key, "value": value, "expire": expire, "success": success}


@router.post("/cache/{key}/json")
async def set_cache_json(
    key: str,
    value: dict[str, Any],
    redis_client: Redis = Depends(get_redis),
    expire: int | None = None,
) -> dict[str, Any]:
    """Set JSON value in cache."""
    cache = RedisCache(redis_client)
    success = await cache.set_json(key, value, expire)
    return {"key": key, "value": value, "expire": expire, "success": success}


@router.get("/cache/{key}/json")
async def get_cache_json(
    key: str, redis_client: Redis = Depends(get_redis)
) -> dict[str, Any]:
    """Get JSON value from cache."""
    cache = RedisCache(redis_client)
    value = await cache.get_json(key)
    return {"key": key, "value": value, "found": value is not None}


@router.post("/cache/{key}/increment")
async def increment_cache_value(
    key: str, amount: int = 1, redis_client: Redis = Depends(get_redis)
) -> dict[str, Any]:
    """Increment numeric value in cache."""
    cache = RedisCache(redis_client)
    new_value = await cache.increment(key, amount)
    return {"key": key, "increment": amount, "new_value": new_value}


@router.delete("/cache/{key}")
async def delete_cache_value(
    key: str, redis_client: Redis = Depends(get_redis)
) -> dict[str, Any]:
    """Delete value from cache."""
    cache = RedisCache(redis_client)
    success = await cache.delete(key)
    return {"key": key, "deleted": success}


@router.get("/cache")
async def list_cache_keys(
    redis_client: Redis = Depends(get_redis), pattern: str = "*"
) -> dict[str, Any]:
    """List cache keys matching pattern."""
    cache = RedisCache(redis_client)
    keys = await cache.get_keys(pattern)
    return {"pattern": pattern, "keys": keys, "count": len(keys)}


@router.post("/session")
async def create_session(redis_client: Redis = Depends(get_redis)) -> dict[str, str]:
    """Create new session with unique ID."""
    session_id = generate_session_id()
    cache = RedisCache(redis_client)

    # Store session metadata
    session_data = {
        "session_id": session_id,
        "created_at": datetime.utcnow().isoformat(),
        "status": "active",
    }

    await cache.set_json(
        session_cache_key(session_id, "metadata"), session_data, expire=3600
    )

    return {"session_id": session_id, "status": "created"}


@router.get("/session/{session_id}")
async def get_session(
    session_id: str, redis_client: Redis = Depends(get_redis)
) -> dict[str, Any]:
    """Get session data."""
    cache = RedisCache(redis_client)
    metadata = await cache.get_json(session_cache_key(session_id, "metadata"))

    if not metadata:
        return {"session_id": session_id, "found": False}

    return {"session_id": session_id, "found": True, "metadata": metadata}


def session_cache_key(session_id: str, key: str) -> str:
    """Generate session-specific cache key."""
    return cache_key("session", session_id, key)
