"""Pydantic schemas for request/response validation."""

from app.schemas.auth import (
    MessageResponse,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenPayload,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.schemas.permission import (
    PermissionAssign,
    PermissionCreate,
    PermissionListResponse,
    PermissionResponse,
)
from app.schemas.role import (
    RoleCreate,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
)
from app.schemas.user import UserInDB, UserProfile, UserUpdate
from app.schemas.user_role import (
    RoleBrief,
    UserRoleAssign,
    UserRoleBulkAssign,
    UserRoleResponse,
    UserRolesResponse,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "TokenPayload",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChange",
    "MessageResponse",
    # User
    "UserUpdate",
    "UserProfile",
    "UserInDB",
    # Role
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleListResponse",
    # Permission
    "PermissionCreate",
    "PermissionResponse",
    "PermissionListResponse",
    "PermissionAssign",
    # User Role
    "UserRoleAssign",
    "UserRoleBulkAssign",
    "UserRoleResponse",
    "UserRolesResponse",
    "RoleBrief",
]
