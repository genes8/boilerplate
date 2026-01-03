"""Unit tests for RBACService."""

import pytest
from uuid import uuid4

from app.models.permission import Permission, PermissionScope
from app.models.role import Role
from app.models.user import User
from app.services.rbac import RBACService


@pytest.mark.asyncio
async def test_has_permission_with_exact_match(db_session):
    """Test has_permission with exact resource/action match."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permission
    permission = Permission(
        resource="documents",
        action="read",
        scope=PermissionScope.ALL.value,
    )
    db_session.add(permission)
    await db_session.flush()

    # Create role and assign permission
    role = Role(name="TestRole", description="Test role")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test permission check
    rbac = RBACService(db_session)
    result = await rbac.has_permission(user, "documents", "read", PermissionScope.ALL.value)
    assert result is True

    # Test with different action
    result = await rbac.has_permission(user, "documents", "write", PermissionScope.ALL.value)
    assert result is False


@pytest.mark.asyncio
async def test_has_permission_with_wildcard(db_session):
    """Test has_permission with wildcard action."""
    # Create test user
    user = User(
        email="test2@example.com",
        username="testuser2",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permission with wildcard action
    permission = Permission(
        resource="documents",
        action="*",
        scope=PermissionScope.ALL.value,
    )
    db_session.add(permission)
    await db_session.flush()

    # Create role and assign permission
    role = Role(name="WildcardRole", description="Wildcard role")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test permission check with wildcard
    rbac = RBACService(db_session)
    result = await rbac.has_permission(user, "documents", "read", PermissionScope.ALL.value)
    assert result is True

    result = await rbac.has_permission(user, "documents", "write", PermissionScope.ALL.value)
    assert result is True

    result = await rbac.has_permission(user, "documents", "delete", PermissionScope.ALL.value)
    assert result is True


@pytest.mark.asyncio
async def test_has_permission_scope_hierarchy(db_session):
    """Test permission scope hierarchy (own < team < all)."""
    # Create test user
    user = User(
        email="test3@example.com",
        username="testuser3",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permission with 'all' scope
    permission = Permission(
        resource="documents",
        action="read",
        scope=PermissionScope.ALL.value,
    )
    db_session.add(permission)
    await db_session.flush()

    # Create role and assign permission
    role = Role(name="AllScopeRole", description="All scope role")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test that 'all' scope permission satisfies 'own' scope requirement
    rbac = RBACService(db_session)
    result = await rbac.has_permission(user, "documents", "read", PermissionScope.OWN.value)
    assert result is True

    # Test that 'all' scope permission satisfies 'team' scope requirement
    result = await rbac.has_permission(user, "documents", "read", PermissionScope.TEAM.value)
    assert result is True

    # Test that 'all' scope permission satisfies 'all' scope requirement
    result = await rbac.has_permission(user, "documents", "read", PermissionScope.ALL.value)
    assert result is True


@pytest.mark.asyncio
async def test_has_role(db_session):
    """Test has_role method."""
    # Create test user
    user = User(
        email="test4@example.com",
        username="testuser4",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create role
    role = Role(name="Admin", description="Admin role")
    db_session.add(role)
    await db_session.flush()

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test role check
    rbac = RBACService(db_session)
    result = await rbac.has_role(user, "Admin")
    assert result is True

    result = await rbac.has_role(user, "User")
    assert result is False


@pytest.mark.asyncio
async def test_has_any_role(db_session):
    """Test has_any_role method."""
    # Create test user
    user = User(
        email="test5@example.com",
        username="testuser5",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create roles
    admin_role = Role(name="Admin", description="Admin role")
    manager_role = Role(name="Manager", description="Manager role")
    db_session.add(admin_role)
    db_session.add(manager_role)
    await db_session.flush()

    # Assign only Admin role
    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test has_any_role
    rbac = RBACService(db_session)
    result = await rbac.has_any_role(user, ["Admin", "Super Admin"])
    assert result is True

    result = await rbac.has_any_role(user, ["Manager", "User"])
    assert result is False


@pytest.mark.asyncio
async def test_is_admin(db_session):
    """Test is_admin method."""
    # Create test user with Admin role
    user = User(
        email="test6@example.com",
        username="testuser6",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    admin_role = Role(name="Admin", description="Admin role")
    db_session.add(admin_role)
    await db_session.flush()

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.commit()

    rbac = RBACService(db_session)
    result = await rbac.is_admin(user)
    assert result is True


@pytest.mark.asyncio
async def test_is_super_admin(db_session):
    """Test is_super_admin method."""
    # Create test user with Super Admin role
    user = User(
        email="test7@example.com",
        username="testuser7",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    superadmin_role = Role(name="Super Admin", description="Super Admin role", is_system=True)
    db_session.add(superadmin_role)
    await db_session.flush()

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=superadmin_role.id)
    db_session.add(user_role)
    await db_session.commit()

    rbac = RBACService(db_session)
    result = await rbac.is_super_admin(user)
    assert result is True


@pytest.mark.asyncio
async def test_get_user_permissions(db_session):
    """Test get_user_permissions method."""
    # Create test user
    user = User(
        email="test8@example.com",
        username="testuser8",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create multiple permissions
    perm1 = Permission(resource="documents", action="read", scope=PermissionScope.OWN.value)
    perm2 = Permission(resource="documents", action="write", scope=PermissionScope.OWN.value)
    perm3 = Permission(resource="users", action="read", scope=PermissionScope.ALL.value)
    db_session.add_all([perm1, perm2, perm3])
    await db_session.flush()

    # Create role and assign permissions
    role = Role(name="TestRole2", description="Test role 2")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    for perm in [perm1, perm2, perm3]:
        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
        db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test get_user_permissions
    rbac = RBACService(db_session)
    permissions = await rbac.get_user_permissions(user)

    assert len(permissions) == 3
    permission_strings = [f"{p['resource']}:{p['action']}:{p['scope']}" for p in permissions]
    assert "documents:read:own" in permission_strings
    assert "documents:write:own" in permission_strings
    assert "users:read:all" in permission_strings


@pytest.mark.asyncio
async def test_get_user_roles(db_session):
    """Test get_user_roles method."""
    # Create test user
    user = User(
        email="test9@example.com",
        username="testuser9",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create multiple roles
    role1 = Role(name="Admin", description="Admin role")
    role2 = Role(name="Manager", description="Manager role")
    db_session.add_all([role1, role2])
    await db_session.flush()

    # Assign roles to user
    from app.models.user_role import UserRole
    user_role1 = UserRole(user_id=user.id, role_id=role1.id)
    user_role2 = UserRole(user_id=user.id, role_id=role2.id)
    db_session.add_all([user_role1, user_role2])
    await db_session.commit()

    # Test get_user_roles
    rbac = RBACService(db_session)
    roles = await rbac.get_user_roles(user)

    assert len(roles) == 2
    role_names = [r["name"] for r in roles]
    assert "Admin" in role_names
    assert "Manager" in role_names


@pytest.mark.asyncio
async def test_has_any_permission(db_session):
    """Test has_any_permission method."""
    # Create test user
    user = User(
        email="test10@example.com",
        username="testuser10",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permission
    permission = Permission(
        resource="documents",
        action="read",
        scope=PermissionScope.OWN.value,
    )
    db_session.add(permission)
    await db_session.flush()

    # Create role and assign permission
    role = Role(name="Reader", description="Reader role")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test has_any_permission
    rbac = RBACService(db_session)
    result = await rbac.has_any_permission(
        user,
        [
            ("documents", "read", PermissionScope.OWN.value),
            ("documents", "write", PermissionScope.OWN.value),
        ],
    )
    assert result is True


@pytest.mark.asyncio
async def test_has_all_permissions(db_session):
    """Test has_all_permissions method."""
    # Create test user
    user = User(
        email="test11@example.com",
        username="testuser11",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permissions
    perm1 = Permission(resource="documents", action="read", scope=PermissionScope.OWN.value)
    perm2 = Permission(resource="documents", action="write", scope=PermissionScope.OWN.value)
    db_session.add_all([perm1, perm2])
    await db_session.flush()

    # Create role and assign permissions
    role = Role(name="Editor", description="Editor role")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    for perm in [perm1, perm2]:
        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
        db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Test has_all_permissions
    rbac = RBACService(db_session)
    result = await rbac.has_all_permissions(
        user,
        [
            ("documents", "read", PermissionScope.OWN.value),
            ("documents", "write", PermissionScope.OWN.value),
        ],
    )
    assert result is True

    # Test with missing permission
    result = await rbac.has_all_permissions(
        user,
        [
            ("documents", "read", PermissionScope.OWN.value),
            ("documents", "delete", PermissionScope.OWN.value),
        ],
    )
    assert result is False


@pytest.mark.asyncio
async def test_invalidate_user_cache(db_session):
    """Test invalidate_user_cache method."""
    # Create test user
    user = User(
        email="test12@example.com",
        username="testuser12",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create permission
    permission = Permission(
        resource="documents",
        action="read",
        scope=PermissionScope.OWN.value,
    )
    db_session.add(permission)
    await db_session.flush()

    # Create role and assign permission
    role = Role(name="TestRole3", description="Test role 3")
    db_session.add(role)
    await db_session.flush()

    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Get permissions (should cache)
    rbac = RBACService(db_session)
    permissions1 = await rbac.get_user_permissions(user)

    # Invalidate cache
    await rbac.invalidate_user_cache(user.id)

    # Get permissions again (should fetch from DB)
    permissions2 = await rbac.get_user_permissions(user)

    assert len(permissions1) == len(permissions2)
