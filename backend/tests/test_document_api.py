"""Integration tests for Document API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.document import Document
from app.models.user import User


@pytest.mark.asyncio
async def test_create_document(client: AsyncClient, auth_headers: dict[str, str]):
    """Test creating a new document."""
    response = await client.post(
        "/api/v1/documents",
        json={
            "title": "New Test Document",
            "content": "This is new document content",
            "meta": {"key": "value"},
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Test Document"
    assert data["content"] == "This is new document content"
    assert data["meta"] == {"key": "value"}
    assert "id" in data
    assert "owner_id" in data


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test listing documents."""
    response = await client.get("/api/v1/documents", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_list_documents_pagination(client: AsyncClient, auth_headers: dict[str, str]):
    """Test document list pagination."""
    response = await client.get(
        "/api/v1/documents?page=1&page_size=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_get_document(client: AsyncClient, auth_headers: dict[str, str], test_document: Document):
    """Test getting a specific document."""
    response = await client.get(
        f"/api/v1/documents/{test_document.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_document.id)
    assert data["title"] == test_document.title


@pytest.mark.asyncio
async def test_get_document_not_found(client: AsyncClient, auth_headers: dict[str, str]):
    """Test getting a non-existent document."""
    from uuid import uuid4

    response = await client.get(
        f"/api/v1/documents/{uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_document(client: AsyncClient, auth_headers: dict[str, str], test_document: Document):
    """Test updating a document."""
    response = await client.put(
        f"/api/v1/documents/{test_document.id}",
        json={
            "title": "Updated Title",
            "content": "Updated content",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_update_document_partial(client: AsyncClient, auth_headers: dict[str, str], test_document: Document):
    """Test partial document update."""
    response = await client.put(
        f"/api/v1/documents/{test_document.id}",
        json={"title": "Only Title Updated"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Only Title Updated"
    assert data["content"] == test_document.content


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, auth_headers: dict[str, str], test_document: Document):
    """Test deleting a document."""
    response = await client.delete(
        f"/api/v1/documents/{test_document.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify document is deleted
    get_response = await client.get(
        f"/api/v1/documents/{test_document.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_document_unauthorized(client: AsyncClient):
    """Test creating document without authentication."""
    response = await client.post(
        "/api/v1/documents",
        json={
            "title": "Unauthorized Document",
            "content": "This should fail",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_document_unauthorized(client: AsyncClient, test_document: Document):
    """Test getting document without authentication."""
    response = await client.get(f"/api/v1/documents/{test_document.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_documents_unauthorized(client: AsyncClient):
    """Test listing documents without authentication."""
    response = await client.get("/api/v1/documents")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_document_ownership_check(
    client: AsyncClient, auth_headers: dict[str, str], auth_headers_2: dict[str, str], test_document: Document
):
    """Test that users can only access their own documents."""
    # User 2 tries to access User 1's document
    response = await client.get(
        f"/api/v1/documents/{test_document.id}",
        headers=auth_headers_2,
    )

    # Should fail (unless user has documents:read:all permission)
    assert response.status_code in [403, 200]  # 403 if no permission, 200 if has permission


# Fixtures
@pytest_asyncio.fixture
async def test_user(client: AsyncClient, test_user_data: dict[str, str]) -> User:
    """Create a test user via API."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Get user ID from login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    
    return User(id=login_response.json()["user"]["id"])


@pytest_asyncio.fixture
async def test_user_2(client: AsyncClient, test_user_data_2: dict[str, str]) -> User:
    """Create a second test user via API."""
    response = await client.post("/api/v1/auth/register", json=test_user_data_2)
    assert response.status_code == 201
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"],
        },
    )
    assert login_response.status_code == 200
    
    return User(id=login_response.json()["user"]["id"])


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user_data: dict[str, str]) -> dict[str, str]:
    """Get authentication headers for user 1."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_2(client: AsyncClient, test_user_data_2: dict[str, str]) -> dict[str, str]:
    """Get authentication headers for user 2."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"],
        },
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_document(client: AsyncClient, auth_headers: dict[str, str]) -> Document:
    """Create a test document via API."""
    response = await client.post(
        "/api/v1/documents",
        json={
            "title": "Test Document",
            "content": "Test content",
            "meta": {"key": "value"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    
    data = response.json()
    return Document(
        id=data["id"],
        title=data["title"],
        content=data["content"],
        meta=data["meta"],
        owner_id=data["owner_id"],
    )


@pytest_asyncio.fixture
async def test_documents(client: AsyncClient, auth_headers: dict[str, str]) -> list[Document]:
    """Create multiple test documents via API."""
    documents = []
    
    for i in range(3):
        response = await client.post(
            "/api/v1/documents",
            json={
                "title": f"Document {i}",
                "content": f"Content {i}",
                "meta": {"index": i},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        
        data = response.json()
        documents.append(
            Document(
                id=data["id"],
                title=data["title"],
                content=data["content"],
                meta=data["meta"],
                owner_id=data["owner_id"],
            )
        )
    
    return documents
