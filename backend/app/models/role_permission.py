"""Role-Permission association table for RBAC."""

from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class RolePermission(Base, TimestampMixin):
    """
    Association table for Role-Permission many-to-many relationship.

    Attributes:
        role_id: Foreign key to roles table
        permission_id: Foreign key to permissions table
    """

    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
