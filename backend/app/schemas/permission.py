"""Permission schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.permission import PermissionScope


class PermissionBase(BaseModel):
    """Base schema for permission."""

    resource: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Resource name (e.g., users, documents, roles)",
    )
    action: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Action name (e.g., create, read, update, delete, *)",
    )
    scope: str = Field(
        default=PermissionScope.OWN.value,
        description="Permission scope (own, team, all)",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Permission description",
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""

    pass


class PermissionResponse(BaseModel):
    """Schema for permission response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resource: str
    action: str
    scope: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    @property
    def permission_string(self) -> str:
        """Return permission as string format."""
        return f"{self.resource}:{self.action}:{self.scope}"


class PermissionListResponse(BaseModel):
    """Schema for permission list response."""

    items: list[PermissionResponse]
    total: int


class PermissionAssign(BaseModel):
    """Schema for assigning permissions to a role."""

    permission_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="List of permission IDs to assign",
    )
