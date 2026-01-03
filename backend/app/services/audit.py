"""Audit logging service for tracking role and permission changes."""

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog
from app.models.role import Role
from app.models.user import User


class AuditService:
    """Service for creating audit logs."""

    @staticmethod
    async def log_role_assigned(
        db: AsyncSession,
        user_id: UUID,
        target_user_id: UUID,
        role_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a role is assigned to a user.

        Args:
            db: Database session
            user_id: ID of the user who performed the action
            target_user_id: ID of the user who received the role
            role_id: ID of the assigned role
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, target_user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :target_user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.ROLE_ASSIGNED.value,
                "entity_type": "user_role",
                "entity_id": str(target_user_id),
                "user_id": user_id,
                "target_user_id": target_user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "target_user_id": str(target_user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_role_removed(
        db: AsyncSession,
        user_id: UUID,
        target_user_id: UUID,
        role_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a role is removed from a user.

        Args:
            db: Database session
            user_id: ID of the user who performed the action
            target_user_id: ID of the user who lost the role
            role_id: ID of the removed role
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, target_user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :target_user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.ROLE_REMOVED.value,
                "entity_type": "user_role",
                "entity_id": str(target_user_id),
                "user_id": user_id,
                "target_user_id": target_user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "target_user_id": str(target_user_id),
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_role_created(
        db: AsyncSession,
        user_id: UUID,
        role_id: UUID,
        role_name: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a new role is created.

        Args:
            db: Database session
            user_id: ID of the user who created the role
            role_id: ID of the created role
            role_name: Name of the created role
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.ROLE_CREATED.value,
                "entity_type": "role",
                "entity_id": str(role_id),
                "user_id": user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "role_name": role_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_role_updated(
        db: AsyncSession,
        user_id: UUID,
        role_id: UUID,
        changes: dict,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a role is updated.

        Args:
            db: Database session
            user_id: ID of the user who updated the role
            role_id: ID of the updated role
            changes: Dictionary of changed fields
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.ROLE_UPDATED.value,
                "entity_type": "role",
                "entity_id": str(role_id),
                "user_id": user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "changes": changes,
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_role_deleted(
        db: AsyncSession,
        user_id: UUID,
        role_id: UUID,
        role_name: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a role is deleted.

        Args:
            db: Database session
            user_id: ID of the user who deleted the role
            role_id: ID of the deleted role
            role_name: Name of the deleted role
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.ROLE_DELETED.value,
                "entity_type": "role",
                "entity_id": str(role_id),
                "user_id": user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "role_name": role_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_permission_assigned(
        db: AsyncSession,
        user_id: UUID,
        role_id: UUID,
        permission_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a permission is assigned to a role.

        Args:
            db: Database session
            user_id: ID of the user who performed the action
            role_id: ID of the role
            permission_id: ID of the permission
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.PERMISSION_ASSIGNED.value,
                "entity_type": "role_permission",
                "entity_id": str(role_id),
                "user_id": user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "permission_id": str(permission_id),
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    @staticmethod
    async def log_permission_removed(
        db: AsyncSession,
        user_id: UUID,
        role_id: UUID,
        permission_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Log when a permission is removed from a role.

        Args:
            db: Database session
            user_id: ID of the user who performed the action
            role_id: ID of the role
            permission_id: ID of the permission
            ip_address: IP address of the requester
            user_agent: User agent string
        """
        await db.execute(
            text("""
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, user_id, role_id,
                    details, ip_address, user_agent
                ) VALUES (
                    :action, :entity_type, :entity_id::text, :user_id, :role_id,
                    :details, :ip_address, :user_agent
                )
            """),
            {
                "action": AuditAction.PERMISSION_REMOVED.value,
                "entity_type": "role_permission",
                "entity_id": str(role_id),
                "user_id": user_id,
                "role_id": role_id,
                "details": json.dumps({
                    "role_id": str(role_id),
                    "permission_id": str(permission_id),
                    "timestamp": datetime.utcnow().isoformat(),
                }),
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )


def get_client_ip(request) -> str:
    """
    Get client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address as string
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
