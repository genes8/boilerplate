"""Document management API endpoints."""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    CurrentActiveUser,
    RBACServiceDep,
    require_permission,
)
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.schemas.auth import MessageResponse
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document import (
    check_document_ownership,
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents",
)
async def list_user_documents(
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
) -> DocumentListResponse:
    """
    List documents.

    - Users with documents:read:all can see all documents
    - Users with documents:read:own can only see their own documents
    """
    # Check if user can read all documents
    can_read_all = await rbac.has_permission(
        current_user, "documents", "read", PermissionScope.ALL.value
    )
    
    # Filter by owner if user can only read own documents
    owner_id = None if can_read_all else current_user.id
    
    documents, total = await list_documents(
        db,
        owner_id=owner_id,
        page=page,
        page_size=page_size,
        include_owner=True,
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
async def create_new_document(
    document_data: DocumentCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("documents", "create", PermissionScope.OWN.value)),
) -> DocumentResponse:
    """
    Create a new document.

    Requires: documents:create permission
    """
    document = await create_document(
        db,
        document_data=document_data,
        owner_id=current_user.id,
    )
    await db.commit()
    
    # Reload with owner relationship
    document = await get_document(db, document.id, include_owner=True)
    
    return DocumentResponse.model_validate(document)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
)
async def get_document_details(
    document_id: UUID,
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Get document details by ID.

    - Users with documents:read:all can read any document
    - Users with documents:read:own can only read their own documents
    """
    document = await get_document(db, document_id, include_owner=True)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check permission
    can_read_all = await rbac.has_permission(
        current_user, "documents", "read", PermissionScope.ALL.value
    )
    
    if not can_read_all and document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this document",
        )
    
    return DocumentResponse.model_validate(document)


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update a document",
)
async def update_existing_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """
    Update a document.

    - Users with documents:update:all can update any document
    - Users with documents:update:own can only update their own documents
    """
    document = await get_document(db, document_id, include_owner=True)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check permission
    can_update_all = await rbac.has_permission(
        current_user, "documents", "update", PermissionScope.ALL.value
    )
    
    if not can_update_all and document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this document",
        )
    
    document = await update_document(db, document, document_data)
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse.model_validate(document)


@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    summary="Delete a document",
)
async def delete_existing_document(
    document_id: UUID,
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    Delete a document.

    - Users with documents:delete:all can delete any document
    - Users with documents:delete:own can only delete their own documents
    """
    document = await get_document(db, document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check permission
    can_delete_all = await rbac.has_permission(
        current_user, "documents", "delete", PermissionScope.ALL.value
    )
    
    if not can_delete_all and document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document",
        )
    
    await delete_document(db, document)
    await db.commit()
    
    return MessageResponse(message="Document deleted successfully")
