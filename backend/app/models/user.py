"""User model for authentication."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.user_role import UserRole

if TYPE_CHECKING:
    from app.models.role import Role


class AuthProvider(str, Enum):
    """Authentication provider types."""

    LOCAL = "local"
    OIDC = "oidc"
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class User(BaseModel):
    """
    User model for authentication and authorization.

    Attributes:
        email: User's email address (unique)
        username: User's username (unique)
        password_hash: Hashed password (nullable for OIDC users)
        auth_provider: Authentication provider (local, oidc, etc.)
        oidc_subject: OIDC subject identifier
        oidc_issuer: OIDC issuer URL
        is_active: Whether the user account is active
        is_verified: Whether the user's email is verified
        last_login_at: Timestamp of last login
    """

    __tablename__ = "users"

    # Core fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,  # Nullable for OIDC users
    )

    # Authentication provider
    auth_provider: Mapped[str] = mapped_column(
        String(50),
        default=AuthProvider.LOCAL.value,
        nullable=False,
    )

    # OIDC fields
    oidc_subject: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    oidc_issuer: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Status flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Tracking
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="foreign(UserRole.role_id) == Role.id",
        lazy="selectin",
        viewonly=True,
    )

    # Indexes
    __table_args__ = (
        Index("idx_users_oidc", "oidc_issuer", "oidc_subject"),
        Index("idx_users_auth_provider", "auth_provider"),
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    @property
    def is_oidc_user(self) -> bool:
        """Check if user authenticated via OIDC."""
        return self.auth_provider != AuthProvider.LOCAL.value

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = func.now()
