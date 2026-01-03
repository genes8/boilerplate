"""Search API endpoints."""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentActiveUser, RBACServiceDep
from app.core.database import get_db
from app.models.permission import PermissionScope
from app.schemas.document import DocumentResponse
from app.schemas.search import (
    SearchHighlight,
    SearchMode,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SearchSuggestion,
    SearchSuggestionsResponse,
)
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search documents",
)
async def search_documents(
    search_request: SearchRequest,
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search documents with various modes.

    **Search Modes:**
    - `simple`: Basic keyword search (default). Words are ANDed together.
    - `phrase`: Exact phrase matching. Matches words in exact order.
    - `fuzzy`: Typo-tolerant search using trigram similarity. Good for OCR errors.
    - `boolean`: Advanced search with AND (&), OR (|), NOT (!) operators.

    **Filters:**
    - `owner_id`: Filter by document owner
    - `date_from`: Filter documents created after this date
    - `date_to`: Filter documents created before this date
    - `meta_filters`: Filter by metadata fields (JSONB contains)

    **Permissions:**
    - Users with documents:read:all can search all documents
    - Users with documents:read:own can only search their own documents
    """
    # Check if user can read all documents
    can_read_all = await rbac.has_permission(
        current_user, "documents", "read", PermissionScope.ALL.value
    )
    
    # Apply owner filter if user can only read own documents
    filters = search_request.filters
    if not can_read_all:
        from app.schemas.search import SearchFilters
        if filters is None:
            filters = SearchFilters(owner_id=current_user.id)
        else:
            # Override owner_id to current user
            filters = SearchFilters(
                owner_id=current_user.id,
                date_from=filters.date_from,
                date_to=filters.date_to,
                meta_filters=filters.meta_filters,
            )
    
    search_service = SearchService(db)
    results, total = await search_service.search(
        query=search_request.query,
        mode=search_request.mode,
        filters=filters,
        page=search_request.page,
        page_size=search_request.page_size,
    )
    
    pages = math.ceil(total / search_request.page_size) if total > 0 else 1
    
    # Convert results to response format
    items = []
    for result in results:
        document = result["document"]
        highlights = [
            SearchHighlight(field=h["field"], fragment=h["fragment"])
            for h in result["highlights"]
        ]
        items.append(
            SearchResultItem(
                document=DocumentResponse.model_validate(document),
                rank=result["rank"],
                highlights=highlights,
            )
        )
    
    return SearchResponse(
        items=items,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
        pages=pages,
        query=search_request.query,
        mode=search_request.mode,
    )


@router.get(
    "/suggestions",
    response_model=SearchSuggestionsResponse,
    summary="Get search suggestions",
)
async def get_search_suggestions(
    current_user: CurrentActiveUser,
    rbac: RBACServiceDep,
    db: AsyncSession = Depends(get_db),
    q: str = Query(..., min_length=1, max_length=100, description="Search query prefix"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of suggestions"),
) -> SearchSuggestionsResponse:
    """
    Get search suggestions/autocomplete based on query prefix.

    Returns document titles that match the query prefix.

    **Permissions:**
    - Users with documents:read:all can get suggestions from all documents
    - Users with documents:read:own can only get suggestions from their own documents
    """
    # Check if user can read all documents
    can_read_all = await rbac.has_permission(
        current_user, "documents", "read", PermissionScope.ALL.value
    )
    
    # Filter by owner if user can only read own documents
    owner_id = None if can_read_all else current_user.id
    
    search_service = SearchService(db)
    suggestions_data = await search_service.get_suggestions(
        query=q,
        limit=limit,
        owner_id=owner_id,
    )
    
    suggestions = [
        SearchSuggestion(
            text=s["text"],
            document_id=s["document_id"],
            field=s["field"],
        )
        for s in suggestions_data
    ]
    
    return SearchSuggestionsResponse(
        suggestions=suggestions,
        query=q,
    )
