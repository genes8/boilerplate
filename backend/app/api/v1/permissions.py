"""Permission management API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentActiveUser,
    require_permission,
)
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.schemas.permission import PermissionListResponse, PermissionResponse
from app.services.rbac import get_all_permissions

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get(
    "",
    response_model=PermissionListResponse,
    summary="List all permissions",
)
async def list_permissions(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("permissions", "read", PermissionScope.ALL.value)),
) -> PermissionListResponse:
    """
    List all available permissions.

    Requires: permissions:read:all permission
    """
    permissions = await get_all_permissions(db)
    return PermissionListResponse(
        items=[PermissionResponse.model_validate(perm) for perm in permissions],
        total=len(permissions),
    )
