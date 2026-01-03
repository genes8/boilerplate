"""Document schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Base schema for document."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Document title",
    )
    content: str | None = Field(
        default=None,
        description="Document content",
    )
    meta: dict = Field(
        default_factory=dict,
        description="Additional metadata as JSON",
    )


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Document title",
    )
    content: str | None = Field(
        default=None,
        description="Document content",
    )
    meta: dict | None = Field(
        default=None,
        description="Additional metadata as JSON",
    )


class OwnerBrief(BaseModel):
    """Brief owner info for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str


class DocumentResponse(BaseModel):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str | None
    meta: dict
    owner_id: UUID
    owner: OwnerBrief | None = None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int
