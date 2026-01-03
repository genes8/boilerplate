"""Search schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.document import DocumentResponse


class SearchMode(str, Enum):
    """Search mode options."""

    SIMPLE = "simple"
    PHRASE = "phrase"
    FUZZY = "fuzzy"
    BOOLEAN = "boolean"


class SearchFilters(BaseModel):
    """Filters for search query."""

    owner_id: UUID | None = Field(
        default=None,
        description="Filter by owner ID",
    )
    date_from: datetime | None = Field(
        default=None,
        description="Filter documents created after this date",
    )
    date_to: datetime | None = Field(
        default=None,
        description="Filter documents created before this date",
    )
    meta_filters: dict | None = Field(
        default=None,
        description="Filter by metadata fields (JSONB contains)",
    )


class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query string",
    )
    mode: SearchMode = Field(
        default=SearchMode.SIMPLE,
        description="Search mode: simple, phrase, fuzzy, or boolean",
    )
    filters: SearchFilters | None = Field(
        default=None,
        description="Optional search filters",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of results per page",
    )


class SearchHighlight(BaseModel):
    """Highlighted text fragment from search result."""

    field: str = Field(description="Field name (title or content)")
    fragment: str = Field(description="Highlighted text fragment with <b> tags")


class SearchResultItem(BaseModel):
    """Single search result item with rank and highlights."""

    document: DocumentResponse
    rank: float = Field(description="Search relevance rank")
    highlights: list[SearchHighlight] = Field(
        default_factory=list,
        description="Highlighted text fragments",
    )


class SearchResponse(BaseModel):
    """Schema for search response."""

    items: list[SearchResultItem]
    total: int = Field(description="Total number of matching documents")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of results per page")
    pages: int = Field(description="Total number of pages")
    query: str = Field(description="Original search query")
    mode: SearchMode = Field(description="Search mode used")


class SearchSuggestion(BaseModel):
    """Search suggestion/autocomplete item."""

    text: str = Field(description="Suggested text")
    document_id: UUID = Field(description="Document ID")
    field: str = Field(description="Field the suggestion came from")


class SearchSuggestionsResponse(BaseModel):
    """Schema for search suggestions response."""

    suggestions: list[SearchSuggestion]
    query: str = Field(description="Original query")
