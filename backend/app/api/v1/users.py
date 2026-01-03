"""User management API endpoints."""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import (
    CurrentActiveUser,
    require_permission,
)
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.user_role import (
    RoleBrief,
    UserRoleAssign,
    UserRoleBulkAssign,
    UserRolesResponse,
)
from app.services.audit import AuditService, get_client_ip
from app.services.rbac import (
    assign_role_to_user,
    get_role_by_id,
    get_users_with_role,
    remove_role_from_user,
)

router = APIRouter(prefix="/users", tags=["users"])


class UserListItem(BaseModel):
    """User list item response."""

    id: UUID
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: str
    roles: List[RoleBrief] = Field(default_factory=list)


class UserListResponse(BaseModel):
    """User list response with pagination."""

    items: List[UserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Get user by ID with roles loaded."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users",
)
async def list_users(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users", "read", PermissionScope.ALL.value)),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by email or username"),
) -> UserListResponse:
    """
    List all users with pagination.

    Requires: users:read:all permission
    """
    query = select(User).options(selectinload(User.roles))

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_pattern)) | (User.username.ilike(search_pattern))
        )

    query = query.order_by(User.created_at.desc())

    total_result = await db.execute(select(User))
    total = len(total_result.scalars().all())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    users = result.scalars().all()

    items = [
        UserListItem(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at.isoformat(),
            roles=[RoleBrief.model_validate(role) for role in user.roles],
        )
        for user in users
    ]

    total_pages = (total + page_size - 1) // page_size

    return UserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{user_id}/roles",
    response_model=UserRolesResponse,
    summary="Get user's roles",
)
async def get_user_roles(
    user_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users", "read", PermissionScope.ALL.value)),
) -> UserRolesResponse:
    """
    Get all roles assigned to a user.

    Requires: users:read:all permission
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserRolesResponse(
        user_id=user.id,
        roles=[RoleBrief.model_validate(role) for role in user.roles],
    )


@router.post(
    "/{user_id}/roles",
    response_model=UserRolesResponse,
    summary="Assign a role to a user",
)
async def assign_user_role(
    user_id: UUID,
    role_data: UserRoleAssign,
    request: Request,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users", "update", PermissionScope.ALL.value)),
) -> UserRolesResponse:
    """
    Assign a role to a user.

    Requires: users:update:all permission
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role = await get_role_by_id(db, role_data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role in user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has the '{role.name}' role",
        )

    await assign_role_to_user(db, user, role, assigned_by=current_user.id)

    await AuditService.log_role_assigned(
        db,
        user_id=current_user.id,
        target_user_id=user.id,
        role_id=role.id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()
    await db.refresh(user)

    return UserRolesResponse(
        user_id=user.id,
        roles=[RoleBrief.model_validate(r) for r in user.roles],
    )


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=UserRolesResponse,
    summary="Remove a role from a user",
)
async def remove_user_role(
    user_id: UUID,
    role_id: UUID,
    request: Request,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users", "update", PermissionScope.ALL.value)),
) -> UserRolesResponse:
    """
    Remove a role from a user.

    Requires: users:update:all permission
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    await remove_role_from_user(db, user, role)

    # Log audit entry
    await AuditService.log_role_removed(
        db,
        user_id=current_user.id,
        target_user_id=user.id,
        role_id=role.id,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )

    await db.commit()
    await db.refresh(user)

    return UserRolesResponse(
        user_id=user.id,
        roles=[RoleBrief.model_validate(r) for r in user.roles],
    )


@router.post(
    "/bulk/roles",
    response_model=MessageResponse,
    summary="Bulk assign a role to multiple users",
)
async def bulk_assign_role(
    bulk_data: UserRoleBulkAssign,
    request: Request,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users", "update", PermissionScope.ALL.value)),
) -> MessageResponse:
    """
    Assign a role to multiple users at once.

    Requires: users:update:all permission
    """
    role = await get_role_by_id(db, bulk_data.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    assigned_count = 0
    for user_id in bulk_data.user_ids:
        user = await get_user_by_id(db, user_id)
        if user:
            await assign_role_to_user(db, user, role, assigned_by=current_user.id)

            # Log audit entry for each assignment
            await AuditService.log_role_assigned(
                db,
                user_id=current_user.id,
                target_user_id=user.id,
                role_id=role.id,
                ip_address=get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
            )
            assigned_count += 1

    await db.commit()

    return MessageResponse(
        message=f"Role assigned to {assigned_count} users"
    )
