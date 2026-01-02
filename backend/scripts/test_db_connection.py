#!/usr/bin/env python3
"""Test database connection script."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


async def test_connection():
    """Test database connection."""
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)
    print(
        f"Database URL: {settings.DATABASE_URL.replace(settings.DATABASE_URL.split(':')[2].split('@')[0], '***')}"
    )
    print()

    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)

        async with engine.connect() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT 1"))
            print("✓ Basic connection: OK")

            # Test PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ PostgreSQL version: {version.split(',')[0]}")

            # Test extensions
            result = await conn.execute(
                text(
                    """
                SELECT extname FROM pg_extension
                WHERE extname IN ('uuid-ossp', 'pg_trgm', 'unaccent', 'vector')
            """
                )
            )
            extensions = [row[0] for row in result.fetchall()]
            print(
                f"✓ Installed extensions: {', '.join(extensions) if extensions else 'None'}"
            )

        await engine.dispose()
        print()
        print("=" * 50)
        print("Connection test PASSED!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"✗ Connection FAILED: {e}")
        print()
        print("Make sure Docker is running:")
        print("  docker compose -f docker-compose.dev.yml up -d")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
