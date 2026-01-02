"""Application configuration using Pydantic Settings."""

from typing import Any, Dict, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Database
    DATABASE_URL: str = Field(
        description="Database connection string",
        examples=["postgresql+asyncpg://user:password@localhost:5432/dbname"],
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    # Security
    JWT_SECRET: str = Field(
        min_length=32,
        description="JWT secret key (minimum 32 characters)",
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration in minutes",
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="JWT refresh token expiration in days",
    )

    # Super Admin
    SUPERADMIN_EMAIL: Optional[str] = Field(
        default=None,
        description="Initial super admin email",
    )
    SUPERADMIN_PASSWORD: Optional[str] = Field(
        default=None,
        description="Initial super admin password (auto-generated if empty)",
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins",
    )

    # File Storage (S3-Compatible)
    S3_ENDPOINT_URL: Optional[str] = Field(
        default=None,
        description="S3-compatible storage endpoint URL",
    )
    S3_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="S3 access key",
    )
    S3_SECRET_KEY: Optional[str] = Field(
        default=None,
        description="S3 secret key",
    )
    S3_BUCKET_NAME: str = Field(
        default="documents",
        description="S3 bucket name",
    )
    S3_REGION: str = Field(
        default="fsn1",
        description="S3 region",
    )

    # Watch Folders
    WATCH_FOLDERS_ENABLED: bool = Field(
        default=False,
        description="Enable watch folders feature",
    )
    WATCH_FOLDERS_ALLOWED_PATHS: list[str] = Field(
        default=["/mnt/imports", "/mnt/shared"],
        description="Allowed paths for watch folders",
    )
    WATCH_FOLDERS_DEFAULT_INTERVAL: int = Field(
        default=60,
        description="Default scan interval in seconds",
    )
    WATCH_FOLDERS_MAX_FILE_SIZE: int = Field(
        default=104857600,  # 100MB
        description="Maximum file size for import in bytes",
    )

    # AI / OpenRouter
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenRouter API key for AI features",
    )
    OPENROUTER_DEFAULT_MODEL: str = Field(
        default="qwen/qwen2.5-vl-72b-instruct",
        description="Default OpenRouter model",
    )

    # OIDC / SSO
    OIDC_ENABLED: bool = Field(
        default=False,
        description="Enable OIDC authentication",
    )
    OIDC_ISSUER_URL: Optional[str] = Field(
        default=None,
        description="OIDC issuer URL",
    )
    OIDC_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="OIDC client ID",
    )
    OIDC_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="OIDC client secret",
    )
    OIDC_REDIRECT_URI: Optional[str] = Field(
        default=None,
        description="OIDC redirect URI",
    )

    # Monitoring
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking",
    )

    # Document Processing
    THUMBNAIL_WIDTH: int = Field(
        default=300,
        description="Thumbnail width in pixels",
    )
    THUMBNAIL_HEIGHT: int = Field(
        default=400,
        description="Thumbnail height in pixels",
    )
    SUPPORTED_FORMATS: list[str] = Field(
        default=["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg", "gif", "xlsx", "xls", "csv"],
        description="Supported document formats",
    )

    @validator("CORS_ORIGINS", pre=True)
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("WATCH_FOLDERS_ALLOWED_PATHS", pre=True)
    @classmethod
    def assemble_watch_folder_paths(cls, v: str | list[str]) -> list[str] | str:
        """Parse watch folder paths from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("SUPPORTED_FORMATS", pre=True)
    @classmethod
    def assemble_supported_formats(cls, v: str | list[str]) -> list[str] | str:
        """Parse supported formats from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def s3_configured(self) -> bool:
        """Check if S3 is properly configured."""
        return all([self.S3_ENDPOINT_URL, self.S3_ACCESS_KEY, self.S3_SECRET_KEY])

    @property
    def openrouter_configured(self) -> bool:
        """Check if OpenRouter is configured."""
        return bool(self.OPENROUTER_API_KEY)

    @property
    def oidc_configured(self) -> bool:
        """Check if OIDC is properly configured."""
        return all(
            [
                self.OIDC_ENABLED,
                self.OIDC_ISSUER_URL,
                self.OIDC_CLIENT_ID,
                self.OIDC_CLIENT_SECRET,
                self.OIDC_REDIRECT_URI,
            ]
        )


# Global settings instance
settings = Settings()
