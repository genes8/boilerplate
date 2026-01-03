"""RBAC (Role-Based Access Control) service for permission checking."""

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import RedisCache, cache_key, redis_client
from app.models.permission import Permission, PermissionScope
from app.models.role import Role
from app.models.user import User

# Cache TTL for permissions (5 minutes)
PERMISSIONS_CACHE_TTL = 300


class RBACService:
    """Service for RBAC operations and permission checking."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = RedisCache(redis_client)

    def _user_permissions_cache_key(self, user_id: UUID) -> str:
        """Generate cache key for user permissions."""
        return cache_key("rbac", "permissions", str(user_id))

    def _user_roles_cache_key(self, user_id: UUID) -> str:
        """Generate cache key for user roles."""
        return cache_key("rbac", "roles", str(user_id))

    async def invalidate_user_cache(self, user_id: UUID) -> None:
        """Invalidate user's permission and role cache."""
        await self.cache.delete(self._user_permissions_cache_key(user_id))
        await self.cache.delete(self._user_roles_cache_key(user_id))

    async def invalidate_role_cache(self, role_id: UUID) -> None:
        """Invalidate cache for all users with a specific role."""
        # Get all users with this role
        result = await self.db.execute(
            select(User)
            .join(User.roles)
            .where(Role.id == role_id)
        )
        users = result.scalars().all()
        for user in users:
            await self.invalidate_user_cache(user.id)

    async def get_user_permissions(self, user: User) -> list[dict]:
        """
        Get all permissions for a user (from all their roles).

        Args:
            user: User object

        Returns:
            List of permission dictionaries with resource, action, scope
        """
        # Try cache first
        cache_key_str = self._user_permissions_cache_key(user.id)
        cached = await self.cache.get_json(cache_key_str)
        if cached is not None:
            return cached

        # Get from database - load user with roles and permissions
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .where(User.id == user.id)
        )
        user_with_roles = result.scalar_one_or_none()

        if not user_with_roles:
            return []

        # Collect all unique permissions
        permissions_set = set()
        permissions_list = []

        for role in user_with_roles.roles:
            for perm in role.permissions:
                perm_key = (perm.resource, perm.action, perm.scope)
                if perm_key not in permissions_set:
                    permissions_set.add(perm_key)
                    permissions_list.append({
                        "id": str(perm.id),
                        "resource": perm.resource,
                        "action": perm.action,
                        "scope": perm.scope,
                    })

        # Cache the result
        await self.cache.set_json(
            cache_key_str,
            permissions_list,
            expire=PERMISSIONS_CACHE_TTL
        )

        return permissions_list

    async def get_user_roles(self, user: User) -> list[dict]:
        """
        Get all roles for a user.

        Args:
            user: User object

        Returns:
            List of role dictionaries with id, name, description
        """
        # Try cache first
        cache_key_str = self._user_roles_cache_key(user.id)
        cached = await self.cache.get_json(cache_key_str)
        if cached is not None:
            return cached

        # Get from database
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user.id)
        )
        user_with_roles = result.scalar_one_or_none()

        if not user_with_roles:
            return []

        roles_list = [
            {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "is_system": role.is_system,
            }
            for role in user_with_roles.roles
        ]

        # Cache the result
        await self.cache.set_json(
            cache_key_str,
            roles_list,
            expire=PERMISSIONS_CACHE_TTL
        )

        return roles_list

    async def has_permission(
        self,
        user: User,
        resource: str,
        action: str,
        required_scope: str = PermissionScope.OWN.value,
    ) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: User object
            resource: Resource name (e.g., "users", "documents")
            action: Action name (e.g., "create", "read", "update", "delete")
            required_scope: Required scope level (own, team, all)

        Returns:
            True if user has the permission, False otherwise
        """
        permissions = await self.get_user_permissions(user)

        # Define scope hierarchy (higher scope includes lower)
        scope_hierarchy = {
            PermissionScope.OWN.value: 0,
            PermissionScope.TEAM.value: 1,
            PermissionScope.ALL.value: 2,
        }

        required_scope_level = scope_hierarchy.get(required_scope, 0)

        for perm in permissions:
            # Check for exact match or wildcard
            resource_match = perm["resource"] == resource or perm["resource"] == "*"
            action_match = perm["action"] == action or perm["action"] == "*"

            if resource_match and action_match:
                # Check scope hierarchy
                perm_scope_level = scope_hierarchy.get(perm["scope"], 0)
                if perm_scope_level >= required_scope_level:
                    return True

        return False

    async def has_any_permission(
        self,
        user: User,
        permissions: list[tuple[str, str, str]],
    ) -> bool:
        """
        Check if user has any of the specified permissions.

        Args:
            user: User object
            permissions: List of (resource, action, scope) tuples

        Returns:
            True if user has at least one permission, False otherwise
        """
        for resource, action, scope in permissions:
            if await self.has_permission(user, resource, action, scope):
                return True
        return False

    async def has_all_permissions(
        self,
        user: User,
        permissions: list[tuple[str, str, str]],
    ) -> bool:
        """
        Check if user has all of the specified permissions.

        Args:
            user: User object
            permissions: List of (resource, action, scope) tuples

        Returns:
            True if user has all permissions, False otherwise
        """
        for resource, action, scope in permissions:
            if not await self.has_permission(user, resource, action, scope):
                return False
        return True

    async def has_role(self, user: User, role_name: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            user: User object
            role_name: Role name to check

        Returns:
            True if user has the role, False otherwise
        """
        roles = await self.get_user_roles(user)
        return any(role["name"] == role_name for role in roles)

    async def has_any_role(self, user: User, role_names: list[str]) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            user: User object
            role_names: List of role names to check

        Returns:
            True if user has at least one role, False otherwise
        """
        roles = await self.get_user_roles(user)
        user_role_names = {role["name"] for role in roles}
        return bool(user_role_names.intersection(role_names))

    async def is_super_admin(self, user: User) -> bool:
        """Check if user is a Super Admin."""
        return await self.has_role(user, "Super Admin")

    async def is_admin(self, user: User) -> bool:
        """Check if user is an Admin or Super Admin."""
        return await self.has_any_role(user, ["Admin", "Super Admin"])


# Role CRUD operations
async def get_role_by_id(db: AsyncSession, role_id: UUID) -> Role | None:
    """Get role by ID."""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.id == role_id)
    )
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """Get role by name."""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.name == name)
    )
    return result.scalar_one_or_none()


async def get_all_roles(db: AsyncSession) -> list[Role]:
    """Get all roles."""
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.name)
    )
    return list(result.scalars().all())


async def create_role(
    db: AsyncSession,
    name: str,
    description: str | None = None,
    is_system: bool = False,
) -> Role:
    """Create a new role."""
    role = Role(
        name=name,
        description=description,
        is_system=is_system,
    )
    db.add(role)
    await db.flush()
    return role


async def update_role(
    db: AsyncSession,
    role: Role,
    name: str | None = None,
    description: str | None = None,
) -> Role:
    """Update a role."""
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    await db.flush()
    return role


async def delete_role(db: AsyncSession, role: Role) -> bool:
    """Delete a role (only non-system roles)."""
    if role.is_system:
        return False
    await db.delete(role)
    await db.flush()
    return True


# Permission CRUD operations
async def get_permission_by_id(db: AsyncSession, permission_id: UUID) -> Permission | None:
    """Get permission by ID."""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    return result.scalar_one_or_none()


async def get_permission(
    db: AsyncSession,
    resource: str,
    action: str,
    scope: str = PermissionScope.OWN.value,
) -> Permission | None:
    """Get permission by resource, action, and scope."""
    result = await db.execute(
        select(Permission).where(
            Permission.resource == resource,
            Permission.action == action,
            Permission.scope == scope,
        )
    )
    return result.scalar_one_or_none()


async def get_all_permissions(db: AsyncSession) -> list[Permission]:
    """Get all permissions."""
    result = await db.execute(
        select(Permission).order_by(Permission.resource, Permission.action)
    )
    return list(result.scalars().all())


async def create_permission(
    db: AsyncSession,
    resource: str,
    action: str,
    scope: str = PermissionScope.OWN.value,
    description: str | None = None,
) -> Permission:
    """Create a new permission."""
    permission = Permission(
        resource=resource,
        action=action,
        scope=scope,
        description=description,
    )
    db.add(permission)
    await db.flush()
    return permission


async def assign_permission_to_role(
    db: AsyncSession,
    role: Role,
    permission: Permission,
) -> None:
    """Assign a permission to a role."""
    if permission not in role.permissions:
        role.permissions.append(permission)
        await db.flush()


async def remove_permission_from_role(
    db: AsyncSession,
    role: Role,
    permission: Permission,
) -> None:
    """Remove a permission from a role."""
    if permission in role.permissions:
        role.permissions.remove(permission)
        await db.flush()


# User-Role operations
async def assign_role_to_user(
    db: AsyncSession,
    user: User,
    role: Role,
    assigned_by: UUID | None = None,
) -> None:
    """Assign a role to a user."""
    if role not in user.roles:
        user.roles.append(role)
        await db.flush()
        # Invalidate cache
        rbac = RBACService(db)
        await rbac.invalidate_user_cache(user.id)


async def remove_role_from_user(
    db: AsyncSession,
    user: User,
    role: Role,
) -> None:
    """Remove a role from a user."""
    if role in user.roles:
        user.roles.remove(role)
        await db.flush()
        # Invalidate cache
        rbac = RBACService(db)
        await rbac.invalidate_user_cache(user.id)


async def get_users_with_role(db: AsyncSession, role_id: UUID) -> list[User]:
    """Get all users with a specific role."""
    result = await db.execute(
        select(User)
        .join(User.roles)
        .where(Role.id == role_id)
    )
    return list(result.scalars().all())
