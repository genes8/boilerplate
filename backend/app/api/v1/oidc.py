"""OIDC (OpenID Connect) authentication endpoints."""

import secrets
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.redis import RedisCache, redis_client
from app.models.user import AuthProvider, User
from app.schemas.auth import TokenResponse
from app.services.jwt import create_tokens, store_refresh_token
from app.services.oidc import oidc_service

router = APIRouter(prefix="/oidc", tags=["OIDC Authentication"])

# State/nonce storage TTL (5 minutes)
OIDC_STATE_TTL = 300


def _get_state_key(state: str) -> str:
    """Get Redis key for OIDC state."""
    return f"oidc:state:{state}"


async def _store_oidc_state(state: str, nonce: str) -> None:
    """Store OIDC state and nonce in Redis."""
    cache = RedisCache(redis_client)
    await cache.set_json(
        _get_state_key(state),
        {"nonce": nonce},
        expire=OIDC_STATE_TTL,
    )


async def _verify_oidc_state(state: str) -> str | None:
    """Verify OIDC state and return nonce."""
    cache = RedisCache(redis_client)
    data = await cache.get_json(_get_state_key(state))
    if data:
        await cache.delete(_get_state_key(state))
        return data.get("nonce")
    return None


@router.get(
    "/authorize",
    summary="Initiate OIDC login",
    response_class=RedirectResponse,
)
async def oidc_authorize() -> RedirectResponse:
    """
    Initiate OIDC authentication flow.

    Redirects user to the OIDC provider's authorization endpoint.
    """
    if not settings.oidc_configured:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OIDC authentication is not configured",
        )

    # Generate state and nonce
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    # Store state and nonce
    await _store_oidc_state(state, nonce)

    # Get authorization URL
    auth_url = oidc_service.get_authorization_url(state=state, nonce=nonce)

    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@router.get(
    "/callback",
    summary="OIDC callback",
    response_model=TokenResponse,
)
async def oidc_callback(
    code: Annotated[str, Query(description="Authorization code")],
    state: Annotated[str, Query(description="State parameter")],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Handle OIDC callback after user authentication.

    - **code**: Authorization code from OIDC provider
    - **state**: State parameter for CSRF protection

    Returns JWT tokens for the authenticated user.
    """
    if not settings.oidc_configured:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="OIDC authentication is not configured",
        )

    # Verify state
    nonce = await _verify_oidc_state(state)
    if nonce is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    try:
        # Exchange code for tokens
        token_response = await oidc_service.exchange_code_for_tokens(
            code=code,
            state=state,
        )

        # Extract user info from ID token
        user_info = oidc_service.extract_user_info(token_response)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with OIDC provider: {str(e)}",
        )

    # Validate required fields
    if not user_info.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OIDC provider did not return subject identifier",
        )

    if not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OIDC provider did not return email address",
        )

    # Find or create user
    user = await _find_or_create_oidc_user(db, user_info)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token, refresh_token, expires_in = create_tokens(user.id)

    # Store refresh token
    await store_refresh_token(user.id, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


async def _find_or_create_oidc_user(
    db: AsyncSession,
    user_info: dict,
) -> User:
    """
    Find existing user or create new one from OIDC user info.

    Args:
        db: Database session.
        user_info: User information from OIDC provider.

    Returns:
        User: The found or created user.
    """
    oidc_subject = user_info["sub"]
    oidc_issuer = user_info.get("issuer", settings.OIDC_ISSUER_URL)
    email = user_info["email"]

    # First, try to find by OIDC subject and issuer
    result = await db.execute(
        select(User).where(
            User.oidc_subject == oidc_subject,
            User.oidc_issuer == oidc_issuer,
        )
    )
    user = result.scalar_one_or_none()

    if user:
        return user

    # Try to find by email (for linking existing accounts)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Link existing account to OIDC
        if user.auth_provider == AuthProvider.LOCAL.value:
            # User has local account, link OIDC
            user.oidc_subject = oidc_subject
            user.oidc_issuer = oidc_issuer
            user.auth_provider = AuthProvider.OIDC.value
            user.is_verified = True  # OIDC email is verified
            await db.commit()
            return user
        else:
            # Already linked to different OIDC
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already associated with another account",
            )

    # Create new user
    username = _generate_username(user_info)

    # Ensure username is unique
    base_username = username
    counter = 1
    while True:
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none() is None:
            break
        username = f"{base_username}{counter}"
        counter += 1

    user = User(
        email=email,
        username=username,
        password_hash=None,  # OIDC users don't have password
        auth_provider=AuthProvider.OIDC.value,
        oidc_subject=oidc_subject,
        oidc_issuer=oidc_issuer,
        is_active=True,
        is_verified=True,  # OIDC email is verified by provider
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


def _generate_username(user_info: dict) -> str:
    """Generate username from OIDC user info."""
    # Try preferred_username first
    if user_info.get("preferred_username"):
        return user_info["preferred_username"].lower().replace(" ", "_")

    # Try name
    if user_info.get("name"):
        return user_info["name"].lower().replace(" ", "_")

    # Try given_name + family_name
    if user_info.get("given_name"):
        username = user_info["given_name"].lower()
        if user_info.get("family_name"):
            username += "_" + user_info["family_name"].lower()
        return username.replace(" ", "_")

    # Fallback to email prefix
    email = user_info.get("email", "")
    return email.split("@")[0].lower().replace(".", "_")
