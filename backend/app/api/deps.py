"""API dependencies for authentication and authorization."""

from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cookies import ACCESS_TOKEN_COOKIE
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.jwt import decode_token, is_token_expired

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


def get_token_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    """
    Extract token from request - first check cookies, then Authorization header.

    Args:
        request: FastAPI request object.
        credentials: HTTP Bearer credentials (optional).

    Returns:
        str | None: The token or None if not found.
    """
    # First, try to get token from HTTP-only cookie
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if token:
        return token

    # Fallback to Authorization header (for API clients)
    if credentials:
        return credentials.credentials

    return None


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials.
        db: Database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If token is invalid, expired, or user not found.
    """
    token = get_token_from_request(request, credentials)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = decode_token(token)

    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_expired(token_payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    try:
        user_id = UUID(token_payload.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current active user.

    Args:
        current_user: The authenticated user.

    Returns:
        User: The active user.

    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    Get the current user if authenticated, None otherwise.

    This dependency does not raise an exception if the user is not authenticated.

    Args:
        request: FastAPI request object.
        credentials: HTTP Bearer credentials.
        db: Database session.

    Returns:
        User | None: The authenticated user or None.
    """
    token = get_token_from_request(request, credentials)
    if token is None:
        return None

    token_payload = decode_token(token)

    if token_payload is None or token_payload.type != "access":
        return None

    if is_token_expired(token_payload):
        return None

    try:
        user_id = UUID(token_payload.sub)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    return user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
