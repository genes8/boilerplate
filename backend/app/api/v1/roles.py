"""Role management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentActiveUser,
    RequireAdmin,
    require_permission,
)
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.schemas.auth import MessageResponse
from app.schemas.permission import PermissionAssign
from app.schemas.role import (
    RoleCreate,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
)
from app.services.rbac import (
    RBACService,
    assign_permission_to_role,
    create_role,
    delete_role,
    get_all_roles,
    get_permission_by_id,
    get_role_by_id,
    get_role_by_name,
    remove_permission_from_role,
    update_role,
)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "",
    response_model=RoleListResponse,
    summary="List all roles",
)
async def list_roles(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "read", PermissionScope.ALL.value)),
) -> RoleListResponse:
    """
    List all roles.

    Requires: roles:read:all permission
    """
    roles = await get_all_roles(db)
    return RoleListResponse(
        items=[RoleResponse.model_validate(role) for role in roles],
        total=len(roles),
    )


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
async def create_new_role(
    role_data: RoleCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "create", PermissionScope.ALL.value)),
) -> RoleResponse:
    """
    Create a new role.

    Requires: roles:create:all permission
    """
    # Check if role name already exists
    existing = await get_role_by_name(db, role_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists",
        )

    role = await create_role(
        db,
        name=role_data.name,
        description=role_data.description,
        is_system=False,
    )
    await db.commit()
    await db.refresh(role)

    return RoleResponse.model_validate(role)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role details",
)
async def get_role(
    role_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "read", PermissionScope.ALL.value)),
) -> RoleResponse:
    """
    Get role details by ID.

    Requires: roles:read:all permission
    """
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return RoleResponse.model_validate(role)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update a role",
)
async def update_existing_role(
    role_id: UUID,
    role_data: RoleUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "update", PermissionScope.ALL.value)),
) -> RoleResponse:
    """
    Update a role.

    Requires: roles:update:all permission
    """
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Check if new name conflicts with existing role
    if role_data.name and role_data.name != role.name:
        existing = await get_role_by_name(db, role_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists",
            )

    role = await update_role(
        db,
        role,
        name=role_data.name,
        description=role_data.description,
    )
    await db.commit()
    await db.refresh(role)

    # Invalidate cache for all users with this role
    rbac = RBACService(db)
    await rbac.invalidate_role_cache(role_id)

    return RoleResponse.model_validate(role)


@router.delete(
    "/{role_id}",
    response_model=MessageResponse,
    summary="Delete a role",
)
async def delete_existing_role(
    role_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "delete", PermissionScope.ALL.value)),
) -> MessageResponse:
    """
    Delete a role (non-system roles only).

    Requires: roles:delete:all permission
    """
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system roles",
        )

    # Invalidate cache for all users with this role before deletion
    rbac = RBACService(db)
    await rbac.invalidate_role_cache(role_id)

    success = await delete_role(db, role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete role",
        )

    await db.commit()
    return MessageResponse(message="Role deleted successfully")


@router.post(
    "/{role_id}/permissions",
    response_model=RoleResponse,
    summary="Assign permissions to a role",
)
async def assign_permissions(
    role_id: UUID,
    permission_data: PermissionAssign,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "update", PermissionScope.ALL.value)),
) -> RoleResponse:
    """
    Assign permissions to a role.

    Requires: roles:update:all permission
    """
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Assign each permission
    for perm_id in permission_data.permission_ids:
        permission = await get_permission_by_id(db, perm_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission {perm_id} not found",
            )
        await assign_permission_to_role(db, role, permission)

    await db.commit()
    await db.refresh(role)

    # Invalidate cache for all users with this role
    rbac = RBACService(db)
    await rbac.invalidate_role_cache(role_id)

    return RoleResponse.model_validate(role)


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    response_model=RoleResponse,
    summary="Remove a permission from a role",
)
async def remove_permission(
    role_id: UUID,
    permission_id: UUID,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("roles", "update", PermissionScope.ALL.value)),
) -> RoleResponse:
    """
    Remove a permission from a role.

    Requires: roles:update:all permission
    """
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    permission = await get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    await remove_permission_from_role(db, role, permission)
    await db.commit()
    await db.refresh(role)

    # Invalidate cache for all users with this role
    rbac = RBACService(db)
    await rbac.invalidate_role_cache(role_id)

    return RoleResponse.model_validate(role)
