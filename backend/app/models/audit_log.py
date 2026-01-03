"""Audit log model for tracking role changes."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditAction(str, Enum):
    """Audit action types."""

    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ROLE_CREATED = "role_created"
    ROLE_UPDATED = "role_updated"
    ROLE_DELETED = "role_deleted"
    PERMISSION_ASSIGNED = "permission_assigned"
    PERMISSION_REMOVED = "permission_removed"


class AuditLog(Base):
    """
    Audit log for tracking role and permission changes.

    Attributes:
        action: Type of action performed
        entity_type: Type of entity affected (user, role, permission)
        entity_id: ID of the affected entity
        user_id: ID of the user who performed the action
        target_user_id: ID of the target user (for role assignments)
        role_id: ID of the role involved
        details: Additional details as JSON
        ip_address: IP address of the requester
        user_agent: User agent string
    """

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    target_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    role_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
        index=True,
    )

    # Indexes
    __table_args__ = (
        Index("idx_audit_logs_action_entity", "action", "entity_type"),
        Index("idx_audit_logs_user_target", "user_id", "target_user_id"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<AuditLog(action={self.action}, entity_type={self.entity_type}, entity_id={self.entity_id})>"
