"""Role model for RBAC."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.user import User


class Role(BaseModel):
    """
    Role model for Role-Based Access Control.

    Attributes:
        name: Role name (unique), e.g., "Admin", "Manager", "User"
        description: Optional description of the role
        is_system: Whether this is a system role (cannot be deleted)
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Role(id={self.id}, name={self.name})>"
