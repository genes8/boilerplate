"""Business logic services."""

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
from app.services.jwt import (
    create_access_token,
    create_refresh_token,
    create_tokens,
    decode_token,
    invalidate_refresh_token,
    is_token_expired,
    store_refresh_token,
    validate_refresh_token,
)
from app.services.search import SearchService
from app.services.security import hash_password, needs_rehash, verify_password

__all__ = [
    "hash_password",
    "verify_password",
    "needs_rehash",
    "create_access_token",
    "create_refresh_token",
    "create_tokens",
    "decode_token",
    "is_token_expired",
    "store_refresh_token",
    "invalidate_refresh_token",
    "validate_refresh_token",
    # Document
    "create_document",
    "get_document",
    "get_document_with_owner_check",
    "update_document",
    "delete_document",
    "list_documents",
    "get_documents_by_owner",
    "check_document_ownership",
    # Search
    "SearchService",
]
