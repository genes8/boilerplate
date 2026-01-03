"""API dependencies for authentication and authorization."""

from functools import wraps
from typing import Annotated, Callable
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cookies import ACCESS_TOKEN_COOKIE
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.jwt import decode_token, is_token_expired
from app.services.rbac import RBACService

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


# RBAC Dependencies
def require_permission(
    resource: str,
    action: str,
    scope: str = PermissionScope.OWN.value,
) -> Callable:
    """
    Dependency factory that requires a specific permission.

    Args:
        resource: Resource name (e.g., "users", "documents")
        action: Action name (e.g., "create", "read", "update", "delete")
        scope: Required scope level (own, team, all)

    Returns:
        Dependency function that checks permission

    Example:
        @router.post("/users")
        async def create_user(
            user: CurrentActiveUser,
            _: None = Depends(require_permission("users", "create", "all")),
        ):
            ...
    """
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac = RBACService(db)
        has_perm = await rbac.has_permission(current_user, resource, action, scope)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}:{action}:{scope}",
            )

    return permission_checker


def require_role(role_name: str) -> Callable:
    """
    Dependency factory that requires a specific role.

    Args:
        role_name: Role name to require

    Returns:
        Dependency function that checks role

    Example:
        @router.delete("/users/{id}")
        async def delete_user(
            user: CurrentActiveUser,
            _: None = Depends(require_role("Admin")),
        ):
            ...
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac = RBACService(db)
        has_role = await rbac.has_role(current_user, role_name)
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}",
            )

    return role_checker


def require_any_role(role_names: list[str]) -> Callable:
    """
    Dependency factory that requires any of the specified roles.

    Args:
        role_names: List of role names (user must have at least one)

    Returns:
        Dependency function that checks roles
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac = RBACService(db)
        has_any = await rbac.has_any_role(current_user, role_names)
        if not has_any:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(role_names)}",
            )

    return role_checker


def require_any_permission(
    permissions: list[tuple[str, str, str]],
) -> Callable:
    """
    Dependency factory that requires any of the specified permissions.

    Args:
        permissions: List of (resource, action, scope) tuples

    Returns:
        Dependency function that checks permissions

    Example:
        @router.get("/reports")
        async def get_reports(
            user: CurrentActiveUser,
            _: None = Depends(require_any_permission([
                ("reports", "read", "all"),
                ("reports", "read", "team"),
            ])),
        ):
            ...
    """
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        rbac = RBACService(db)
        has_any = await rbac.has_any_permission(current_user, permissions)
        if not has_any:
            perm_strings = [f"{r}:{a}:{s}" for r, a, s in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(perm_strings)}",
            )

    return permission_checker


async def get_rbac_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RBACService:
    """Dependency that provides RBAC service."""
    return RBACService(db)


# Type alias for RBAC service dependency
RBACServiceDep = Annotated[RBACService, Depends(get_rbac_service)]


# Admin-only dependency
RequireAdmin = Depends(require_any_role(["Admin", "Super Admin"]))
RequireSuperAdmin = Depends(require_role("Super Admin"))
