"""Seed default roles and permissions for RBAC."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Permission, PermissionScope
from app.models.role import Role
from app.models.role_permission import RolePermission


# Default permissions definition
# Format: (resource, action, scope, description)
DEFAULT_PERMISSIONS = [
    # Users permissions
    ("users", "create", PermissionScope.ALL.value, "Create new users"),
    ("users", "read", PermissionScope.OWN.value, "Read own user profile"),
    ("users", "read", PermissionScope.ALL.value, "Read all users"),
    ("users", "update", PermissionScope.OWN.value, "Update own user profile"),
    ("users", "update", PermissionScope.ALL.value, "Update any user"),
    ("users", "delete", PermissionScope.ALL.value, "Delete users"),
    
    # Roles permissions
    ("roles", "create", PermissionScope.ALL.value, "Create new roles"),
    ("roles", "read", PermissionScope.ALL.value, "Read all roles"),
    ("roles", "update", PermissionScope.ALL.value, "Update roles"),
    ("roles", "delete", PermissionScope.ALL.value, "Delete roles"),
    
    # Permissions permissions
    ("permissions", "read", PermissionScope.ALL.value, "Read all permissions"),
    
    # Documents permissions
    ("documents", "create", PermissionScope.OWN.value, "Create own documents"),
    ("documents", "read", PermissionScope.OWN.value, "Read own documents"),
    ("documents", "read", PermissionScope.TEAM.value, "Read team documents"),
    ("documents", "read", PermissionScope.ALL.value, "Read all documents"),
    ("documents", "update", PermissionScope.OWN.value, "Update own documents"),
    ("documents", "update", PermissionScope.TEAM.value, "Update team documents"),
    ("documents", "update", PermissionScope.ALL.value, "Update all documents"),
    ("documents", "delete", PermissionScope.OWN.value, "Delete own documents"),
    ("documents", "delete", PermissionScope.ALL.value, "Delete all documents"),
    
    # Labels permissions
    ("labels", "create", PermissionScope.OWN.value, "Create own labels"),
    ("labels", "read", PermissionScope.OWN.value, "Read own labels"),
    ("labels", "read", PermissionScope.ALL.value, "Read all labels"),
    ("labels", "update", PermissionScope.OWN.value, "Update own labels"),
    ("labels", "update", PermissionScope.ALL.value, "Update all labels"),
    ("labels", "delete", PermissionScope.OWN.value, "Delete own labels"),
    ("labels", "delete", PermissionScope.ALL.value, "Delete all labels"),
    
    # Watch folders permissions
    ("watch_folders", "create", PermissionScope.OWN.value, "Create own watch folders"),
    ("watch_folders", "read", PermissionScope.OWN.value, "Read own watch folders"),
    ("watch_folders", "read", PermissionScope.ALL.value, "Read all watch folders"),
    ("watch_folders", "update", PermissionScope.OWN.value, "Update own watch folders"),
    ("watch_folders", "update", PermissionScope.ALL.value, "Update all watch folders"),
    ("watch_folders", "delete", PermissionScope.OWN.value, "Delete own watch folders"),
    ("watch_folders", "delete", PermissionScope.ALL.value, "Delete all watch folders"),
    
    # System/Admin permissions
    ("system", "*", PermissionScope.ALL.value, "Full system access (wildcard)"),
]

# Default roles definition
# Format: (name, description, is_system, permission_patterns)
# permission_patterns: list of (resource, action, scope) tuples or "*" for all
DEFAULT_ROLES = [
    (
        "Super Admin",
        "Full system access with all permissions",
        True,
        [("*", "*", PermissionScope.ALL.value)],  # Wildcard - all permissions
    ),
    (
        "Admin",
        "Administrative access to manage users, roles, and system settings",
        True,
        [
            ("users", "*", PermissionScope.ALL.value),
            ("roles", "*", PermissionScope.ALL.value),
            ("permissions", "read", PermissionScope.ALL.value),
            ("documents", "*", PermissionScope.ALL.value),
            ("labels", "*", PermissionScope.ALL.value),
            ("watch_folders", "*", PermissionScope.ALL.value),
        ],
    ),
    (
        "Manager",
        "Team management with access to team resources",
        True,
        [
            ("users", "read", PermissionScope.ALL.value),
            ("documents", "create", PermissionScope.OWN.value),
            ("documents", "read", PermissionScope.TEAM.value),
            ("documents", "update", PermissionScope.TEAM.value),
            ("documents", "delete", PermissionScope.OWN.value),
            ("labels", "create", PermissionScope.OWN.value),
            ("labels", "read", PermissionScope.ALL.value),
            ("labels", "update", PermissionScope.OWN.value),
            ("labels", "delete", PermissionScope.OWN.value),
            ("watch_folders", "create", PermissionScope.OWN.value),
            ("watch_folders", "read", PermissionScope.OWN.value),
            ("watch_folders", "update", PermissionScope.OWN.value),
            ("watch_folders", "delete", PermissionScope.OWN.value),
        ],
    ),
    (
        "User",
        "Standard user with access to own resources",
        True,
        [
            ("users", "read", PermissionScope.OWN.value),
            ("users", "update", PermissionScope.OWN.value),
            ("documents", "create", PermissionScope.OWN.value),
            ("documents", "read", PermissionScope.OWN.value),
            ("documents", "update", PermissionScope.OWN.value),
            ("documents", "delete", PermissionScope.OWN.value),
            ("labels", "create", PermissionScope.OWN.value),
            ("labels", "read", PermissionScope.OWN.value),
            ("labels", "update", PermissionScope.OWN.value),
            ("labels", "delete", PermissionScope.OWN.value),
        ],
    ),
    (
        "Viewer",
        "Read-only access to own resources",
        True,
        [
            ("users", "read", PermissionScope.OWN.value),
            ("documents", "read", PermissionScope.OWN.value),
            ("labels", "read", PermissionScope.OWN.value),
        ],
    ),
]


async def seed_permissions(db: AsyncSession) -> dict[tuple[str, str, str], Permission]:
    """
    Seed default permissions.
    
    Returns:
        Dictionary mapping (resource, action, scope) to Permission objects
    """
    permissions_map: dict[tuple[str, str, str], Permission] = {}
    
    for resource, action, scope, description in DEFAULT_PERMISSIONS:
        # Check if permission already exists
        result = await db.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action == action,
                Permission.scope == scope,
            )
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            permission = Permission(
                resource=resource,
                action=action,
                scope=scope,
                description=description,
            )
            db.add(permission)
            print(f"  Created permission: {resource}:{action}:{scope}")
        
        permissions_map[(resource, action, scope)] = permission
    
    await db.flush()
    return permissions_map


async def seed_roles(
    db: AsyncSession,
    permissions_map: dict[tuple[str, str, str], Permission],
) -> dict[str, Role]:
    """
    Seed default roles with their permissions.
    
    Returns:
        Dictionary mapping role name to Role objects
    """
    roles_map: dict[str, Role] = {}
    
    for name, description, is_system, permission_patterns in DEFAULT_ROLES:
        # Check if role already exists (with permissions loaded)
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name)
        )
        role = result.scalar_one_or_none()
        is_new_role = False
        
        if not role:
            role = Role(
                name=name,
                description=description,
                is_system=is_system,
            )
            db.add(role)
            await db.flush()
            is_new_role = True
            print(f"  Created role: {name}")
        
        # Get current permission IDs for this role
        # For new roles, start with empty set
        if is_new_role:
            existing_perm_ids: set = set()
        else:
            existing_perm_ids = {p.id for p in role.permissions}
        
        # Assign permissions to role using association table directly
        for resource, action, scope in permission_patterns:
            # Handle wildcard permissions
            if resource == "*" and action == "*":
                # Full wildcard - assign ALL permissions
                for perm in permissions_map.values():
                    if perm.id not in existing_perm_ids:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=perm.id,
                        )
                        db.add(role_perm)
                        existing_perm_ids.add(perm.id)
            elif action == "*":
                # Wildcard action - assign all permissions for this resource
                for perm_key, perm in permissions_map.items():
                    if perm_key[0] == resource:
                        if perm.id not in existing_perm_ids:
                            role_perm = RolePermission(
                                role_id=role.id,
                                permission_id=perm.id,
                            )
                            db.add(role_perm)
                            existing_perm_ids.add(perm.id)
            else:
                # Specific permission
                perm_key = (resource, action, scope)
                if perm_key in permissions_map:
                    perm = permissions_map[perm_key]
                    if perm.id not in existing_perm_ids:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=perm.id,
                        )
                        db.add(role_perm)
                        existing_perm_ids.add(perm.id)
        
        roles_map[name] = role
    
    await db.flush()
    return roles_map


async def seed_rbac(db: AsyncSession) -> tuple[dict[str, Role], dict[tuple[str, str, str], Permission]]:
    """
    Seed all default RBAC data (permissions and roles).
    
    Returns:
        Tuple of (roles_map, permissions_map)
    """
    print("Seeding RBAC data...")
    
    # Seed permissions first
    print("Seeding permissions...")
    permissions_map = await seed_permissions(db)
    
    # Seed roles with permissions
    print("Seeding roles...")
    roles_map = await seed_roles(db, permissions_map)
    
    await db.commit()
    print("RBAC seeding complete!")
    
    return roles_map, permissions_map


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """Get a role by name."""
    result = await db.execute(
        select(Role).where(Role.name == name)
    )
    return result.scalar_one_or_none()
