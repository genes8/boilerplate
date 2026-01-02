#!/usr/bin/env python3
"""Test Redis connection script."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.redis import (
    RedisCache,
    cache_key,
    generate_session_id,
    redis_client,
    session_cache_key,
    user_cache_key,
)


async def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("=" * 50)
    print("Redis Connection Test")
    print("=" * 50)
    print("Redis URL: redis://localhost:6380/0")
    print()

    try:
        # Test basic connection
        await redis_client.ping()
        print("✓ Basic connection: OK")

        # Test Redis info
        info = await redis_client.info()
        print(f"✓ Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"✓ Used memory: {info.get('used_memory_human', 'Unknown')}")

        # Test basic operations
        test_key = "test:connection"
        test_value = "Hello Redis!"

        # SET operation
        await redis_client.set(test_key, test_value)
        print("✓ SET operation: OK")

        # GET operation
        retrieved = await redis_client.get(test_key)
        if retrieved == test_value:
            print("✓ GET operation: OK")
        else:
            print(f"✗ GET operation failed: Expected '{test_value}', got '{retrieved}'")
            return False

        # DELETE operation
        deleted = await redis_client.delete(test_key)
        if deleted:
            print("✓ DELETE operation: OK")
        else:
            print("✗ DELETE operation failed")
            return False

        # Test RedisCache class
        cache = RedisCache(redis_client)

        # Test string operations
        await cache.set("test:string", "value", expire=60)
        value = await cache.get("test:string")
        if value == "value":
            print("✓ RedisCache string operations: OK")
        else:
            print("✗ RedisCache string operations failed")
            return False

        # Test JSON operations
        test_data = {"name": "Test", "numbers": [1, 2, 3]}
        await cache.set_json("test:json", test_data, expire=60)
        json_data = await cache.get_json("test:json")
        if json_data == test_data:
            print("✓ RedisCache JSON operations: OK")
        else:
            print("✗ RedisCache JSON operations failed")
            return False

        # Test increment/decrement
        await cache.set("test:counter", 0)
        await cache.increment("test:counter", 5)
        counter = await cache.get("test:counter")
        if counter == "5":
            print("✓ RedisCache increment: OK")
        else:
            print("✗ RedisCache increment failed")
            return False

        # Test cache key generation
        key1 = cache_key("user", "123", "profile")
        key2 = session_cache_key("session123", "data")
        key3 = user_cache_key("user456", "preferences")

        print("✓ Cache key generation:")
        print(f"  - cache_key: {key1}")
        print(f"  - session_cache_key: {key2}")
        print(f"  - user_cache_key: {key3}")

        # Test session ID generation
        session_id = generate_session_id()
        if len(session_id) == 36 and session_id.count("-") == 4:  # UUID format
            print("✓ Session ID generation: OK")
        else:
            print("✗ Session ID generation failed")
            return False

        # Cleanup test data
        await cache.delete_pattern("test:*")

        print()
        print("=" * 50)
        print("Redis test PASSED!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"✗ Redis test FAILED: {e}")
        print()
        print("Make sure Redis is running:")
        print("  docker compose -f docker-compose.dev.yml up -d")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_redis_connection())
    sys.exit(0 if success else 1)
