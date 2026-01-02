"""Rate limiting utilities using Redis."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.core.redis import RedisCache, redis_client

# Rate limit configuration
LOGIN_RATE_LIMIT_REQUESTS = 5  # Max requests
LOGIN_RATE_LIMIT_WINDOW = 60  # Window in seconds (1 minute)
LOGIN_RATE_LIMIT_BLOCK_TIME = 300  # Block time in seconds (5 minutes)


def _get_rate_limit_key(identifier: str, action: str) -> str:
    """Generate rate limit key."""
    return f"rate_limit:{action}:{identifier}"


def _get_block_key(identifier: str, action: str) -> str:
    """Generate block key."""
    return f"rate_limit_block:{action}:{identifier}"


async def check_rate_limit(
    identifier: str,
    action: str,
    max_requests: int = LOGIN_RATE_LIMIT_REQUESTS,
    window_seconds: int = LOGIN_RATE_LIMIT_WINDOW,
    block_seconds: int = LOGIN_RATE_LIMIT_BLOCK_TIME,
) -> tuple[bool, int]:
    """
    Check if request is within rate limit.

    Args:
        identifier: Unique identifier (IP address, email, etc.)
        action: Action being rate limited (login, register, etc.)
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        block_seconds: Block duration after exceeding limit

    Returns:
        tuple: (is_allowed, remaining_requests or seconds_until_unblock)
    """
    cache = RedisCache(redis_client)

    # Check if blocked
    block_key = _get_block_key(identifier, action)
    block_ttl = await cache.ttl(block_key)
    if block_ttl > 0:
        return False, block_ttl

    # Get current request count
    rate_key = _get_rate_limit_key(identifier, action)
    current_count = await cache.get(rate_key)

    if current_count is None:
        # First request in window
        await cache.set(rate_key, "1", expire=window_seconds)
        return True, max_requests - 1

    count = int(current_count)

    if count >= max_requests:
        # Rate limit exceeded, block the identifier
        await cache.set(block_key, "1", expire=block_seconds)
        await cache.delete(rate_key)
        return False, block_seconds

    # Increment counter
    await cache.increment(rate_key)
    return True, max_requests - count - 1


async def reset_rate_limit(identifier: str, action: str) -> None:
    """
    Reset rate limit for an identifier (e.g., after successful login).

    Args:
        identifier: Unique identifier
        action: Action being rate limited
    """
    cache = RedisCache(redis_client)
    rate_key = _get_rate_limit_key(identifier, action)
    block_key = _get_block_key(identifier, action)
    await cache.delete(rate_key)
    await cache.delete(block_key)


class RateLimiter:
    """Rate limiter dependency for FastAPI."""

    def __init__(
        self,
        action: str,
        max_requests: int = LOGIN_RATE_LIMIT_REQUESTS,
        window_seconds: int = LOGIN_RATE_LIMIT_WINDOW,
        block_seconds: int = LOGIN_RATE_LIMIT_BLOCK_TIME,
    ):
        self.action = action
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds

    async def __call__(self, request: Request) -> None:
        """Check rate limit for the request."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Also check X-Forwarded-For header for proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        is_allowed, remaining = await check_rate_limit(
            identifier=client_ip,
            action=self.action,
            max_requests=self.max_requests,
            window_seconds=self.window_seconds,
            block_seconds=self.block_seconds,
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {remaining} seconds.",
                headers={"Retry-After": str(remaining)},
            )


# Pre-configured rate limiters
login_rate_limiter = RateLimiter(
    action="login",
    max_requests=5,
    window_seconds=60,
    block_seconds=300,
)

register_rate_limiter = RateLimiter(
    action="register",
    max_requests=3,
    window_seconds=60,
    block_seconds=600,
)

password_reset_rate_limiter = RateLimiter(
    action="password_reset",
    max_requests=3,
    window_seconds=60,
    block_seconds=600,
)
