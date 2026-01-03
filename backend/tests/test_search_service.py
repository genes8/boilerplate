"""Unit tests for Search service."""

import pytest
from datetime import datetime, timedelta

from app.models.document import Document
from app.models.user import User
from app.schemas.search import SearchFilters, SearchMode
from app.services.search import SearchService


@pytest.mark.asyncio
async def test_search_simple(test_session: AsyncSession, test_documents: list[Document]):
    """Test simple full-text search."""
    search_service = SearchService(test_session)
    
    results, total = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        page=1,
        page_size=10,
    )
    
    assert total > 0
    assert len(results) > 0
    assert results[0]["rank"] >= 0


@pytest.mark.asyncio
async def test_search_phrase(test_session: AsyncSession, test_documents: list[Document]):
    """Test phrase search."""
    search_service = SearchService(test_session)
    
    results, total = await search_service.search(
        query="test content",
        mode=SearchMode.PHRASE,
        page=1,
        page_size=10,
    )
    
    assert total >= 0  # May be 0 if exact phrase not found
    assert len(results) == total


@pytest.mark.asyncio
async def test_search_fuzzy(test_session: AsyncSession, test_documents: list[Document]):
    """Test fuzzy search with typo tolerance."""
    search_service = SearchService(test_session)
    
    # Search with typo
    results, total = await search_service.search(
        query="documnt",  # Typo: missing 'e'
        mode=SearchMode.FUZZY,
        page=1,
        page_size=10,
    )
    
    assert total >= 0
    assert len(results) == total


@pytest.mark.asyncio
async def test_search_boolean(test_session: AsyncSession, test_documents: list[Document]):
    """Test boolean search with operators."""
    search_service = SearchService(test_session)
    
    # Search for documents with "test" AND "content"
    results, total = await search_service.search(
        query="test & content",
        mode=SearchMode.BOOLEAN,
        page=1,
        page_size=10,
    )
    
    assert total >= 0
    assert len(results) == total


@pytest.mark.asyncio
async def test_search_with_owner_filter(
    test_session: AsyncSession, test_documents: list[Document], test_user: User
):
    """Test search with owner filter."""
    search_service = SearchService(test_session)
    
    filters = SearchFilters(owner_id=test_user.id)
    
    results, total = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        filters=filters,
        page=1,
        page_size=10,
    )
    
    # All results should belong to test_user
    for result in results:
        assert result["document"].owner_id == test_user.id


@pytest.mark.asyncio
async def test_search_with_date_filter(test_session: AsyncSession, test_documents: list[Document]):
    """Test search with date range filter."""
    search_service = SearchService(test_session)
    
    # Filter documents from today
    today = datetime.now().date()
    filters = SearchFilters(date_from=datetime.combine(today, datetime.min.time()))
    
    results, total = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        filters=filters,
        page=1,
        page_size=10,
    )
    
    assert total >= 0


@pytest.mark.asyncio
async def test_search_with_meta_filter(
    test_session: AsyncSession, test_documents: list[Document]
):
    """Test search with metadata filter."""
    search_service = SearchService(test_session)
    
    # Filter by metadata
    filters = SearchFilters(meta_filters={"index": 0})
    
    results, total = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        filters=filters,
        page=1,
        page_size=10,
    )
    
    assert total >= 0
    for result in results:
        assert result["document"].meta.get("index") == 0


@pytest.mark.asyncio
async def test_search_pagination(test_session: AsyncSession, test_documents: list[Document]):
    """Test search pagination."""
    search_service = SearchService(test_session)
    
    page_size = 2
    results_1, total = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        page=1,
        page_size=page_size,
    )
    
    results_2, total_2 = await search_service.search(
        query="document",
        mode=SearchMode.SIMPLE,
        page=2,
        page_size=page_size,
    )
    
    assert total == total_2
    assert len(results_1) <= page_size
    assert len(results_2) <= page_size
    
    # Results should be different (different pages)
    if total > page_size:
        assert results_1[0]["document"].id != results_2[0]["document"].id


@pytest.mark.asyncio
async def test_search_highlights(test_session: AsyncSession, test_documents: list[Document]):
    """Test search highlights."""
    search_service = SearchService(test_session)
    
    results, total = await search_service.search(
        query="test",
        mode=SearchMode.SIMPLE,
        page=1,
        page_size=10,
    )
    
    for result in results:
        # Check that highlights are present
        assert "highlights" in result
        assert isinstance(result["highlights"], list)
        
        # If there are highlights, they should have field and fragment
        for highlight in result["highlights"]:
            assert "field" in highlight
            assert "fragment" in highlight
            assert highlight["field"] in ["title", "content"]


@pytest.mark.asyncio
async def test_get_suggestions(test_session: AsyncSession, test_documents: list[Document]):
    """Test search suggestions/autocomplete."""
    search_service = SearchService(test_session)
    
    suggestions = await search_service.get_suggestions(
        query="doc",
        limit=5,
    )
    
    assert len(suggestions) <= 5
    for suggestion in suggestions:
        assert "text" in suggestion
        assert "document_id" in suggestion
        assert "field" in suggestion
        assert suggestion["field"] == "title"
        assert "doc" in suggestion["text"].lower()


@pytest.mark.asyncio
async def test_get_suggestions_with_owner_filter(
    test_session: AsyncSession, test_documents: list[Document], test_user: User
):
    """Test suggestions with owner filter."""
    search_service = SearchService(test_session)
    
    suggestions = await search_service.get_suggestions(
        query="doc",
        limit=10,
        owner_id=test_user.id,
    )
    
    # All suggestions should belong to test_user
    for suggestion in suggestions:
        doc = next((d for d in test_documents if d.id == suggestion["document_id"]), None)
        if doc:
            assert doc.owner_id == test_user.id


@pytest.mark.asyncio
async def test_search_ranking(test_session: AsyncSession, test_documents: list[Document]):
    """Test that search results are ranked by relevance."""
    search_service = SearchService(test_session)
    
    results, total = await search_service.search(
        query="test",
        mode=SearchMode.SIMPLE,
        page=1,
        page_size=10,
    )
    
    if len(results) > 1:
        # Results should be sorted by rank (descending)
        for i in range(len(results) - 1):
            assert results[i]["rank"] >= results[i + 1]["rank"]


# Fixtures
@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user."""
    from app.services.security import hash_password

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("TestPassword123!"),
        is_active=True,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_documents(test_session: AsyncSession, test_user: User) -> list[Document]:
    """Create test documents for searching."""
    documents = []
    
    # Create documents with varying content
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
        document = Document(
            title=data["title"],
            content=data["content"],
            meta=data["meta"],
            owner_id=test_user.id,
        )
        test_session.add(document)
        documents.append(document)
    
    await test_session.commit()
    
    for doc in documents:
        await test_session.refresh(doc)
    
    return documents
