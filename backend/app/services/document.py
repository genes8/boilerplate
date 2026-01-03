"""Document CRUD service."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate


async def create_document(
    db: AsyncSession,
    document_data: DocumentCreate,
    owner_id: UUID,
) -> Document:
    """
    Create a new document.

    Args:
        db: Database session
        document_data: Document creation data
        owner_id: ID of the document owner

    Returns:
        Created document
    """
    document = Document(
        title=document_data.title,
        content=document_data.content,
        meta=document_data.meta,
        owner_id=owner_id,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    return document


async def get_document(
    db: AsyncSession,
    document_id: UUID,
    include_owner: bool = False,
) -> Document | None:
    """
    Get document by ID.

    Args:
        db: Database session
        document_id: Document ID
        include_owner: Whether to load owner relationship

    Returns:
        Document if found, None otherwise
    """
    query = select(Document).where(Document.id == document_id)
    
    if include_owner:
        query = query.options(selectinload(Document.owner))
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_document_with_owner_check(
    db: AsyncSession,
    document_id: UUID,
    owner_id: UUID,
) -> Document | None:
    """
    Get document by ID with ownership check.

    Args:
        db: Database session
        document_id: Document ID
        owner_id: Expected owner ID

    Returns:
        Document if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.owner))
        .where(
            Document.id == document_id,
            Document.owner_id == owner_id,
        )
    )
    return result.scalar_one_or_none()


async def update_document(
    db: AsyncSession,
    document: Document,
    document_data: DocumentUpdate,
) -> Document:
    """
    Update a document.

    Args:
        db: Database session
        document: Document to update
        document_data: Update data

    Returns:
        Updated document
    """
    update_dict = document_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(document, field, value)
    
    await db.flush()
    await db.refresh(document)
    return document


async def delete_document(
    db: AsyncSession,
    document: Document,
) -> bool:
    """
    Delete a document.

    Args:
        db: Database session
        document: Document to delete

    Returns:
        True if deleted successfully
    """
    await db.delete(document)
    await db.flush()
    return True


async def list_documents(
    db: AsyncSession,
    owner_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    include_owner: bool = False,
) -> tuple[list[Document], int]:
    """
    List documents with pagination.

    Args:
        db: Database session
        owner_id: Filter by owner ID (optional)
        page: Page number (1-indexed)
        page_size: Number of items per page
        include_owner: Whether to load owner relationship

    Returns:
        Tuple of (documents list, total count)
    """
    # Base query
    query = select(Document)
    count_query = select(func.count(Document.id))
    
    # Apply owner filter
    if owner_id is not None:
        query = query.where(Document.owner_id == owner_id)
        count_query = count_query.where(Document.owner_id == owner_id)
    
    # Include owner if requested
    if include_owner:
        query = query.options(selectinload(Document.owner))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    documents = list(result.scalars().all())
    
    return documents, total


async def get_documents_by_owner(
    db: AsyncSession,
    owner_id: UUID,
) -> list[Document]:
    """
    Get all documents owned by a user.

    Args:
        db: Database session
        owner_id: Owner user ID

    Returns:
        List of documents
    """
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == owner_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def check_document_ownership(
    db: AsyncSession,
    document_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Check if a user owns a document.

    Args:
        db: Database session
        document_id: Document ID
        user_id: User ID

    Returns:
        True if user owns the document, False otherwise
    """
    result = await db.execute(
        select(func.count(Document.id))
        .where(
            Document.id == document_id,
            Document.owner_id == user_id,
        )
    )
    count = result.scalar() or 0
    return count > 0
