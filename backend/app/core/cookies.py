"""Cookie utilities for HTTP-only token storage."""

from typing import Literal

from fastapi import Response

from app.config import settings

# Cookie names
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    access_token_max_age: int | None = None,
    refresh_token_max_age: int | None = None,
) -> None:
    """
    Set HTTP-only authentication cookies.

    Args:
        response: FastAPI response object.
        access_token: JWT access token.
        refresh_token: JWT refresh token.
        access_token_max_age: Access token max age in seconds (default from settings).
        refresh_token_max_age: Refresh token max age in seconds (default from settings).
    """
    if access_token_max_age is None:
        access_token_max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    if refresh_token_max_age is None:
        refresh_token_max_age = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # Determine SameSite value
    samesite: Literal["lax", "strict", "none"] = "lax"
    if settings.COOKIE_SAMESITE.lower() == "strict":
        samesite = "strict"
    elif settings.COOKIE_SAMESITE.lower() == "none":
        samesite = "none"

    # Set access token cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=access_token_max_age,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=samesite,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )

    # Set refresh token cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=refresh_token_max_age,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=samesite,
        domain=settings.COOKIE_DOMAIN,
        path="/api/v1/auth",  # Only sent to auth endpoints
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies.

    Args:
        response: FastAPI response object.
    """
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path="/api/v1/auth",
        domain=settings.COOKIE_DOMAIN,
    )
