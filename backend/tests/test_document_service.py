"""Unit tests for Document service."""

import pytest
from sqlalchemy import select
from uuid import uuid4

from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document import (
    check_document_ownership,
    create_document,
    delete_document,
    get_document,
    get_document_with_owner_check,
    get_documents_by_owner,
    list_documents,
    update_document,
)


@pytest.mark.asyncio
async def test_create_document(test_session: AsyncSession, test_user: User):
    """Test creating a new document."""
    document_data = DocumentCreate(
        title="Test Document",
        content="This is test content",
        meta={"key": "value"},
    )

    document = await create_document(
        test_session,
        document_data=document_data,
        owner_id=test_user.id,
    )

    assert document.id is not None
    assert document.title == "Test Document"
    assert document.content == "This is test content"
    assert document.meta == {"key": "value"}
    assert document.owner_id == test_user.id


@pytest.mark.asyncio
async def test_get_document(test_session: AsyncSession, test_document: Document):
    """Test getting a document by ID."""
    document = await get_document(test_session, test_document.id)

    assert document is not None
    assert document.id == test_document.id
    assert document.title == test_document.title


@pytest.mark.asyncio
async def test_get_document_not_found(test_session: AsyncSession):
    """Test getting a non-existent document."""
    document = await get_document(test_session, uuid4())

    assert document is None


@pytest.mark.asyncio
async def test_get_document_with_owner_check_success(
    test_session: AsyncSession, test_document: Document, test_user: User
):
    """Test getting document with ownership check (success)."""
    document = await get_document_with_owner_check(
        test_session,
        test_document.id,
        test_user.id,
    )

    assert document is not None
    assert document.id == test_document.id


@pytest.mark.asyncio
async def test_get_document_with_owner_check_failure(
    test_session: AsyncSession, test_document: Document, test_user_2: User
):
    """Test getting document with ownership check (wrong owner)."""
    document = await get_document_with_owner_check(
        test_session,
        test_document.id,
        test_user_2.id,
    )

    assert document is None


@pytest.mark.asyncio
async def test_update_document(test_session: AsyncSession, test_document: Document):
    """Test updating a document."""
    update_data = DocumentUpdate(
        title="Updated Title",
        content="Updated content",
        meta={"new_key": "new_value"},
    )

    updated_document = await update_document(
        test_session,
        test_document,
        update_data,
    )

    assert updated_document.title == "Updated Title"
    assert updated_document.content == "Updated content"
    assert updated_document.meta == {"new_key": "new_value"}


@pytest.mark.asyncio
async def test_update_document_partial(test_session: AsyncSession, test_document: Document):
    """Test partial update of a document."""
    update_data = DocumentUpdate(title="Only Title Updated")

    updated_document = await update_document(
        test_session,
        test_document,
        update_data,
    )

    assert updated_document.title == "Only Title Updated"
    assert updated_document.content == test_document.content


@pytest.mark.asyncio
async def test_delete_document(test_session: AsyncSession, test_document: Document):
    """Test deleting a document."""
    document_id = test_document.id

    success = await delete_document(test_session, test_document)

    assert success is True

    # Verify document is deleted
    document = await get_document(test_session, document_id)
    assert document is None


@pytest.mark.asyncio
async def test_list_documents_all(test_session: AsyncSession, test_documents: list[Document]):
    """Test listing all documents."""
    documents, total = await list_documents(
        test_session,
        owner_id=None,
        page=1,
        page_size=10,
    )

    assert len(documents) == len(test_documents)
    assert total == len(test_documents)


@pytest.mark.asyncio
async def test_list_documents_by_owner(
    test_session: AsyncSession, test_documents: list[Document], test_user: User
):
    """Test listing documents filtered by owner."""
    # Filter documents by test_user
    user_documents = [d for d in test_documents if d.owner_id == test_user.id]

    documents, total = await list_documents(
        test_session,
        owner_id=test_user.id,
        page=1,
        page_size=10,
    )

    assert len(documents) == len(user_documents)
    assert total == len(user_documents)
    for doc in documents:
        assert doc.owner_id == test_user.id


@pytest.mark.asyncio
async def test_list_documents_pagination(
    test_session: AsyncSession, test_documents: list[Document]
):
    """Test document list pagination."""
    page_size = 2
    documents, total = await list_documents(
        test_session,
        page=1,
        page_size=page_size,
    )

    assert len(documents) == page_size
    assert total == len(test_documents)


@pytest.mark.asyncio
async def test_get_documents_by_owner(
    test_session: AsyncSession, test_documents: list[Document], test_user: User
):
    """Test getting all documents by owner."""
    user_documents = [d for d in test_documents if d.owner_id == test_user.id]

    documents = await get_documents_by_owner(test_session, test_user.id)

    assert len(documents) == len(user_documents)
    for doc in documents:
        assert doc.owner_id == test_user.id


@pytest.mark.asyncio
async def test_check_document_ownership_true(
    test_session: AsyncSession, test_document: Document, test_user: User
):
    """Test checking document ownership (true)."""
    has_ownership = await check_document_ownership(
        test_session,
        test_document.id,
        test_user.id,
    )

    assert has_ownership is True


@pytest.mark.asyncio
async def test_check_document_ownership_false(
    test_session: AsyncSession, test_document: Document, test_user_2: User
):
    """Test checking document ownership (false)."""
    has_ownership = await check_document_ownership(
        test_session,
        test_document.id,
        test_user_2.id,
    )

    assert has_ownership is False


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
async def test_user_2(test_session: AsyncSession) -> User:
    """Create a second test user."""
    from app.services.security import hash_password

    user = User(
        email="test2@example.com",
        username="testuser2",
        password_hash=hash_password("TestPassword456!"),
        is_active=True,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_document(test_session: AsyncSession, test_user: User) -> Document:
    """Create a test document."""
    document = Document(
        title="Test Document",
        content="Test content",
        meta={"key": "value"},
        owner_id=test_user.id,
    )
    test_session.add(document)
    await test_session.commit()
    await test_session.refresh(document)
    return document


@pytest_asyncio.fixture
async def test_documents(
    test_session: AsyncSession, test_user: User, test_user_2: User
) -> list[Document]:
    """Create multiple test documents."""
    documents = []
    for i in range(5):
        owner = test_user if i < 3 else test_user_2
        document = Document(
            title=f"Document {i}",
            content=f"Content {i}",
            meta={"index": i},
            owner_id=owner.id,
        )
        test_session.add(document)
        documents.append(document)
    
    await test_session.commit()
    
    for doc in documents:
        await test_session.refresh(doc)
    
    return documents
