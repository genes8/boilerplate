"""Role schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    """Base schema for role."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Role name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Role description",
    )


class RoleCreate(RoleBase):
    """Schema for creating a role."""

    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Role name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Role description",
    )


class PermissionBrief(BaseModel):
    """Brief permission info for role response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resource: str
    action: str
    scope: str

    @property
    def permission_string(self) -> str:
        """Return permission as string format."""
        return f"{self.resource}:{self.action}:{self.scope}"


class RoleResponse(BaseModel):
    """Schema for role response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    is_system: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionBrief] = Field(default_factory=list)


class RoleListResponse(BaseModel):
    """Schema for role list response."""

    items: list[RoleResponse]
    total: int
