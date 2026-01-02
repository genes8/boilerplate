"""User schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (alphanumeric, underscore, hyphen)",
    )
    email: EmailStr | None = Field(default=None, description="User email address")


class UserProfile(BaseModel):
    """Schema for user profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    auth_provider: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None


class UserInDB(BaseModel):
    """Schema for user in database (internal use)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    password_hash: str | None
    auth_provider: str
    oidc_subject: str | None
    oidc_issuer: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
