"""Database initialization utilities."""

import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.seed_rbac import get_role_by_name, seed_rbac
from app.models.user import AuthProvider, User
from app.services.security import hash_password


async def create_superadmin(db: AsyncSession) -> None:
    """
    Create Super Admin user if it doesn't exist.

    Reads credentials from environment variables:
    - SUPERADMIN_EMAIL: Email for super admin (required)
    - SUPERADMIN_PASSWORD: Password (auto-generated if empty)

    Assigns Super Admin role to the user.
    """
    email = settings.SUPERADMIN_EMAIL

    if not email:
        # No super admin email configured, skip
        return

    # Check if super admin already exists
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Check if user has Super Admin role
        superadmin_role = await get_role_by_name(db, "Super Admin")
        if superadmin_role and superadmin_role not in existing_user.roles:
            existing_user.roles.append(superadmin_role)
            await db.commit()
            print(f"✅ Super Admin role assigned to: {email}")
        else:
            print(f"✅ Super Admin already exists: {email}")
        return

    # Get or generate password
    password = settings.SUPERADMIN_PASSWORD
    password_generated = False

    if not password:
        password = secrets.token_urlsafe(16)
        password_generated = True

    # Create super admin user
    user = User(
        email=email,
        username="admin",
        password_hash=hash_password(password),
        auth_provider=AuthProvider.LOCAL.value,
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    await db.flush()

    # Assign Super Admin role
    superadmin_role = await get_role_by_name(db, "Super Admin")
    if superadmin_role:
        user.roles.append(superadmin_role)

    await db.commit()
    await db.refresh(user)

    # Print credentials
    print("=" * 60)
    print("  🔐 SUPER ADMIN CREATED")
    print("=" * 60)
    print(f"  Email: {email}")
    if password_generated:
        print(f"  Password: {password}")
        print("  ⚠️  SAVE THIS PASSWORD - IT WON'T BE SHOWN AGAIN!")
    else:
        print("  Password: (from environment variable)")
    print("  Role: Super Admin")
    print("=" * 60)


async def init_database(db: AsyncSession) -> None:
    """
    Initialize database with required data.

    This function is called on application startup.
    """
    # Seed default roles and permissions
    await seed_rbac(db)

    # Create super admin if configured
    await create_superadmin(db)
