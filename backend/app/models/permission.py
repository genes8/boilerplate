"""Permission model for RBAC."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.role import Role


class PermissionScope(str, Enum):
    """Permission scope types."""

    OWN = "own"  # User can only access their own resources
    TEAM = "team"  # User can access team resources
    ALL = "all"  # User can access all resources


class Permission(BaseModel):
    """
    Permission model for fine-grained access control.

    Attributes:
        resource: Resource name, e.g., "users", "documents", "roles"
        action: Action name, e.g., "create", "read", "update", "delete", "*"
        scope: Permission scope (own, team, all)
        description: Optional description of the permission
    """

    __tablename__ = "permissions"

    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    scope: Mapped[str] = mapped_column(
        String(20),
        default=PermissionScope.OWN.value,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("idx_permissions_resource_action", "resource", "action"),
        Index(
            "idx_permissions_unique",
            "resource",
            "action",
            "scope",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Permission(id={self.id}, resource={self.resource}, action={self.action}, scope={self.scope})>"

    @property
    def permission_string(self) -> str:
        """Return permission as string format: resource:action:scope."""
        return f"{self.resource}:{self.action}:{self.scope}"
