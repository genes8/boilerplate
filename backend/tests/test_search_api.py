"""Integration tests for Search API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.document import Document


@pytest.mark.asyncio
async def test_search_simple(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test simple search."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "query" in data
    assert data["query"] == "test"
    assert data["mode"] == "simple"


@pytest.mark.asyncio
async def test_search_phrase(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test phrase search."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test content",
            "mode": "phrase",
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "phrase"


@pytest.mark.asyncio
async def test_search_fuzzy(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test fuzzy search."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "documnt",  # Typo
            "mode": "fuzzy",
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "fuzzy"


@pytest.mark.asyncio
async def test_search_boolean(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test boolean search."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test & content",
            "mode": "boolean",
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "boolean"


@pytest.mark.asyncio
async def test_search_with_filters(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test search with filters."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
            "filters": {
                "meta_filters": {"index": 0},
            },
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_search_pagination(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test search pagination."""
    page_size = 2
    
    response_1 = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
            "page": 1,
            "page_size": page_size,
        },
        headers=auth_headers,
    )
    
    response_2 = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
            "page": 2,
            "page_size": page_size,
        },
        headers=auth_headers,
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    
    data_1 = response_1.json()
    data_2 = response_2.json()
    
    assert data_1["total"] == data_2["total"]
    assert len(data_1["items"]) <= page_size
    assert len(data_2["items"]) <= page_size


@pytest.mark.asyncio
async def test_search_highlights(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test search highlights."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    
    for item in data["items"]:
        assert "document" in item
        assert "rank" in item
        assert "highlights" in item
        assert isinstance(item["highlights"], list)


@pytest.mark.asyncio
async def test_search_unauthorized(client: AsyncClient):
    """Test search without authentication."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "simple",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_suggestions(client: AsyncClient, auth_headers: dict[str, str], test_documents: list[Document]):
    """Test search suggestions."""
    response = await client.get(
        "/api/v1/search/suggestions?q=doc&limit=5",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert "query" in data
    assert data["query"] == "doc"
    assert len(data["suggestions"]) <= 5
    
    for suggestion in data["suggestions"]:
        assert "text" in suggestion
        assert "document_id" in suggestion
        assert "field" in suggestion


@pytest.mark.asyncio
async def test_get_suggestions_unauthorized(client: AsyncClient):
    """Test suggestions without authentication."""
    response = await client.get("/api/v1/search/suggestions?q=test")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_empty_query(client: AsyncClient, auth_headers: dict[str, str]):
    """Test search with empty query."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "",
            "mode": "simple",
        },
        headers=auth_headers,
    )

    # Should fail validation
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_invalid_mode(client: AsyncClient, auth_headers: dict[str, str]):
    """Test search with invalid mode."""
    response = await client.post(
        "/api/v1/search",
        json={
            "query": "test",
            "mode": "invalid",
        },
        headers=auth_headers,
    )

    # Should fail validation
    assert response.status_code == 422


# Fixtures
@pytest_asyncio.fixture
async def test_user(client: AsyncClient, test_user_data: dict[str, str]) -> User:
    """Create a test user via API."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
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
async def auth_headers(client: AsyncClient, test_user_data: dict[str, str]) -> dict[str, str]:
    """Get authentication headers."""
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
async def test_documents(client: AsyncClient, auth_headers: dict[str, str]) -> list[Document]:
    """Create test documents via API."""
    documents = []
    
    test_data = [
        {
            "title": "Test Document One",
            "content": "This is test content with multiple words",
            "meta": {"index": 0, "category": "test"},
        },
        {
            "title": "Another Document",
            "content": "Different content here",
            "meta": {"index": 1, "category": "other"},
        },
        {
            "title": "Test Document Two",
            "content": "More test content for searching",
            "meta": {"index": 2, "category": "test"},
        },
        {
            "title": "Sample Document",
            "content": "Sample text for testing",
            "meta": {"index": 3, "category": "sample"},
        },
        {
            "title": "Test Document Three",
            "content": "Final test document content",
            "meta": {"index": 4, "category": "test"},
        },
    ]
    
    for data in test_data:
        response = await client.post(
            "/api/v1/documents",
            json=data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        
        doc_data = response.json()
        documents.append(
            Document(
                id=doc_data["id"],
                title=doc_data["title"],
                content=doc_data["content"],
                meta=doc_data["meta"],
                owner_id=doc_data["owner_id"],
            )
        )
    
    return documents
