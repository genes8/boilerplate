"""User-Role schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRoleAssign(BaseModel):
    """Schema for assigning a role to a user."""

    role_id: UUID = Field(..., description="Role ID to assign")


class UserRoleBulkAssign(BaseModel):
    """Schema for bulk assigning roles to users."""

    user_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="List of user IDs",
    )
    role_id: UUID = Field(..., description="Role ID to assign")


class RoleBrief(BaseModel):
    """Brief role info for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None


class UserRoleResponse(BaseModel):
    """Schema for user role response."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role_id: UUID
    role: RoleBrief
    assigned_at: datetime
    assigned_by: UUID | None


class UserRolesResponse(BaseModel):
    """Schema for user's roles response."""

    user_id: UUID
    roles: list[RoleBrief]
