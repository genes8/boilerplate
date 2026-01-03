"""Authentication API endpoints."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentActiveUser
from app.core.cookies import REFRESH_TOKEN_COOKIE, clear_auth_cookies, set_auth_cookies
from app.core.database import get_db
from app.core.rate_limit import (
    login_rate_limiter,
    password_reset_rate_limiter,
    register_rate_limiter,
    reset_rate_limit,
)
from app.models.user import AuthProvider, User
from app.schemas.auth import (
    MessageResponse,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.jwt import (
    create_tokens,
    decode_token,
    invalidate_refresh_token,
    is_token_expired,
    store_refresh_token,
    validate_refresh_token,
)
from app.services.email import email_service
from app.services.password_reset import (
    create_password_reset_token,
    invalidate_password_reset_token,
    verify_password_reset_token,
)
from app.services.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    dependencies=[Depends(register_rate_limiter)],
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **username**: Username (3-100 chars, alphanumeric, underscore, hyphen)
    - **password**: Password (minimum 8 characters)
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        auth_provider=AuthProvider.LOCAL.value,
        is_active=True,
        is_verified=False,  # Email verification not implemented yet
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access tokens",
    dependencies=[Depends(login_rate_limiter)],
)
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    - **email**: User's email address
    - **password**: User's password

    Returns access token and refresh token.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Check if user has password (not OIDC user)
    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use SSO to login",
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Create tokens
    access_token, refresh_token, expires_in = create_tokens(user.id)

    # Store refresh token in Redis
    await store_refresh_token(user.id, refresh_token)

    # Reset rate limit on successful login
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    await reset_rate_limit(client_ip, "login")

    # Set HTTP-only cookies
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    token_request: RefreshTokenRequest | None = None,
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Token can be provided via:
    - HTTP-only cookie (preferred)
    - Request body: **refresh_token**
    """
    # Get refresh token from cookie or request body
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not refresh_token_value and token_request:
        refresh_token_value = token_request.refresh_token

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    # Decode refresh token
    token_payload = decode_token(refresh_token_value)

    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    if is_token_expired(token_payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # Get user ID from token
    try:
        user_id = UUID(token_payload.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Validate refresh token against stored token
    is_valid = await validate_refresh_token(user_id, refresh_token_value)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token, new_refresh_token, expires_in = create_tokens(user.id)

    # Store new refresh token
    await store_refresh_token(user.id, new_refresh_token)

    # Set HTTP-only cookies
    set_auth_cookies(response, access_token, new_refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout and invalidate tokens",
)
async def logout(
    response: Response,
    current_user: CurrentActiveUser,
) -> MessageResponse:
    """
    Logout current user and invalidate refresh token.

    Requires authentication.
    """
    # Invalidate refresh token
    await invalidate_refresh_token(current_user.id)

    # Clear HTTP-only cookies
    clear_auth_cookies(response)

    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_me(
    current_user: CurrentActiveUser,
) -> User:
    """
    Get current authenticated user information.

    Requires authentication.
    """
    return current_user


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
)
async def change_password(
    password_data: PasswordChange,
    current_user: CurrentActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Change current user's password.

    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)

    Requires authentication.
    """
    # Check if user has password (not OIDC user)
    if current_user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for SSO users",
        )

    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    await db.commit()

    # Invalidate all refresh tokens (force re-login)
    await invalidate_refresh_token(current_user.id)

    return MessageResponse(message="Password changed successfully")


@router.post(
    "/password/reset",
    response_model=MessageResponse,
    summary="Request password reset",
    dependencies=[Depends(password_reset_rate_limiter)],
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Request a password reset email.

    - **email**: User's email address

    Note: For security reasons, this endpoint always returns success
    even if the email doesn't exist in the system.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == reset_request.email))
    user = result.scalar_one_or_none()

    if user is not None:
        # Only create token for local auth users
        if user.password_hash is not None and user.is_active:
            # Create password reset token
            token = await create_password_reset_token(user.id, user.email)

            # Send password reset email
            await email_service.send_password_reset_email(
                to_email=user.email,
                reset_token=token,
                username=user.username,
            )

    # Always return success for security (don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/password/reset/confirm",
    response_model=MessageResponse,
    summary="Confirm password reset",
)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Reset password using reset token.

    - **token**: Password reset token from email
    - **new_password**: New password (minimum 8 characters)
    """
    # Verify token
    token_data = await verify_password_reset_token(request.token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Get user from token data
    try:
        user_id = UUID(token_data["user_id"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or inactive",
        )

    # Update password
    user.password_hash = hash_password(request.new_password)
    await db.commit()

    # Invalidate reset token
    await invalidate_password_reset_token(request.token, user_id)

    # Invalidate all refresh tokens (force re-login with new password)
    await invalidate_refresh_token(user_id)

    return MessageResponse(message="Password has been reset successfully")
