"""Document model for full-text search."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class Document(BaseModel):
    """
    Document model with full-text search support.

    Attributes:
        title: Document title (weighted 'A' in search)
        content: Document content (weighted 'B' in search)
        meta: Additional metadata as JSONB
        owner_id: Foreign key to the document owner
        search_vector: PostgreSQL tsvector for full-text search (generated column)
    """

    __tablename__ = "documents"

    # Core fields
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    meta: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False,
    )

    # Owner relationship
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Full-text search vector
    # Note: This is a generated column in PostgreSQL, created via migration
    # The actual generation expression is defined in the migration
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )

    # Indexes for full-text search
    __table_args__ = (
        # GIN index for full-text search
        Index(
            "idx_documents_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
        # Trigram indexes for fuzzy search
        Index(
            "idx_documents_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "idx_documents_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Document(id={self.id}, title={self.title})>"
