"""Integration tests for RBAC API endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.models.permission import Permission, PermissionScope
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreate
from app.schemas.permission import PermissionAssign


@pytest.mark.asyncio
async def test_list_roles_as_admin(async_client: AsyncClient, admin_token_headers):
    """Test listing all roles as admin."""
    response = await async_client.get(
        "/api/v1/roles",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_create_role_as_admin(async_client: AsyncClient, admin_token_headers):
    """Test creating a new role as admin."""
    role_data = {
        "name": "TestRole",
        "description": "Test role for integration testing",
    }
    response = await async_client.post(
        "/api/v1/roles",
        json=role_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TestRole"
    assert data["description"] == "Test role for integration testing"
    assert data["is_system"] is False


@pytest.mark.asyncio
async def test_create_role_duplicate_name(async_client: AsyncClient, admin_token_headers):
    """Test creating a role with duplicate name."""
    role_data = {
        "name": "Admin",
        "description": "Duplicate admin role",
    }
    response = await async_client.post(
        "/api/v1/roles",
        json=role_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_role_by_id(async_client: AsyncClient, admin_token_headers, db_session):
    """Test getting a role by ID."""
    # Create test role
    role = Role(name="GetTestRole", description="Test role for get")
    db_session.add(role)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/roles/{role.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(role.id)
    assert data["name"] == "GetTestRole"


@pytest.mark.asyncio
async def test_get_role_not_found(async_client: AsyncClient, admin_token_headers):
    """Test getting a non-existent role."""
    fake_id = uuid4()
    response = await async_client.get(
        f"/api/v1/roles/{fake_id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test updating a role."""
    # Create test role
    role = Role(name="UpdateTestRole", description="Original description")
    db_session.add(role)
    await db_session.commit()

    update_data = {
        "description": "Updated description",
    }
    response = await async_client.put(
        f"/api/v1/roles/{role.id}",
        json=update_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test deleting a non-system role."""
    # Create test role
    role = Role(name="DeleteTestRole", description="Test role for deletion", is_system=False)
    db_session.add(role)
    await db_session.commit()

    response = await async_client.delete(
        f"/api/v1/roles/{role.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]


@pytest.mark.asyncio
async def test_delete_system_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test that system roles cannot be deleted."""
    # Create system role
    role = Role(name="SystemRole", description="System role", is_system=True)
    db_session.add(role)
    await db_session.commit()

    response = await async_client.delete(
        f"/api/v1/roles/{role.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_assign_permissions_to_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test assigning permissions to a role."""
    # Create test role
    role = Role(name="PermTestRole", description="Test role for permissions")
    db_session.add(role)
    await db_session.flush()

    # Create test permissions
    perm1 = Permission(resource="documents", action="read", scope=PermissionScope.OWN.value)
    perm2 = Permission(resource="documents", action="write", scope=PermissionScope.OWN.value)
    db_session.add_all([perm1, perm2])
    await db_session.commit()

    # Assign permissions
    assign_data = {
        "permission_ids": [str(perm1.id), str(perm2.id)],
    }
    response = await async_client.post(
        f"/api/v1/roles/{role.id}/permissions",
        json=assign_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["permissions"]) >= 2


@pytest.mark.asyncio
async def test_remove_permission_from_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test removing a permission from a role."""
    # Create test role
    role = Role(name="RemovePermRole", description="Test role for removing permissions")
    db_session.add(role)
    await db_session.flush()

    # Create test permission
    permission = Permission(resource="documents", action="read", scope=PermissionScope.OWN.value)
    db_session.add(permission)
    await db_session.flush()

    # Assign permission
    from app.models.role_permission import RolePermission
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)
    await db_session.commit()

    # Remove permission
    response = await async_client.delete(
        f"/api/v1/roles/{role.id}/permissions/{permission.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_permissions(async_client: AsyncClient, admin_token_headers):
    """Test listing all permissions."""
    response = await async_client.get(
        "/api/v1/permissions",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_get_user_roles(async_client: AsyncClient, admin_token_headers, db_session):
    """Test getting user's roles."""
    # Create test user
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Assign role
    role = Role(name="UserRoleTest", description="Test role")
    db_session.add(role)
    await db_session.flush()

    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/users/{user.id}/roles",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert len(data["roles"]) > 0


@pytest.mark.asyncio
async def test_assign_role_to_user(async_client: AsyncClient, admin_token_headers, db_session):
    """Test assigning a role to a user."""
    # Create test user
    user = User(
        email="assignuser@example.com",
        username="assignuser",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create test role
    role = Role(name="AssignRoleTest", description="Test role for assignment")
    db_session.add(role)
    await db_session.commit()

    # Assign role
    assign_data = {"role_id": str(role.id)}
    response = await async_client.post(
        f"/api/v1/users/{user.id}/roles",
        json=assign_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["roles"]) > 0


@pytest.mark.asyncio
async def test_remove_role_from_user(async_client: AsyncClient, admin_token_headers, db_session):
    """Test removing a role from a user."""
    # Create test user
    user = User(
        email="removeuser@example.com",
        username="removeuser",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Create test role
    role = Role(name="RemoveRoleTest", description="Test role for removal")
    db_session.add(role)
    await db_session.flush()

    # Assign role
    from app.models.user_role import UserRole
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Remove role
    response = await async_client.delete(
        f"/api/v1/users/{user.id}/roles/{role.id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_bulk_assign_role(async_client: AsyncClient, admin_token_headers, db_session):
    """Test bulk assigning a role to multiple users."""
    # Create test users
    user1 = User(
        email="bulkuser1@example.com",
        username="bulkuser1",
        password_hash="hash",
        is_active=True,
    )
    user2 = User(
        email="bulkuser2@example.com",
        username="bulkuser2",
        password_hash="hash",
        is_active=True,
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    # Create test role
    role = Role(name="BulkRoleTest", description="Test role for bulk assignment")
    db_session.add(role)
    await db_session.commit()

    # Bulk assign role
    bulk_data = {
        "user_ids": [str(user1.id), str(user2.id)],
        "role_id": str(role.id),
    }
    response = await async_client.post(
        "/api/v1/users/bulk/roles",
        json=bulk_data,
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "assigned to 2 users" in data["message"]


@pytest.mark.asyncio
async def test_unauthorized_access_to_roles(async_client: AsyncClient):
    """Test that unauthorized access is rejected."""
    response = await async_client.get("/api/v1/roles")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_forbidden_without_permission(async_client: AsyncClient, user_token_headers):
    """Test that users without permissions are forbidden."""
    response = await async_client.get(
        "/api/v1/roles",
        headers=user_token_headers,
    )
    assert response.status_code == 403
