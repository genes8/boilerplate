"""FastAPI application main entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.test_redis import router as test_redis_router
from app.api.v1 import api_v1_router
from app.config import settings
from app.core.database import async_session_maker, close_db, engine
from app.core.init_db import init_database
from app.core.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Enterprise Boilerplate Backend...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")

    # Test database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection: OK")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    # Initialize Redis connection
    try:
        await init_redis()
    except Exception as e:
        print(f"❌ Redis initialization failed: {e}")

    # Initialize database (create super admin, etc.)
    try:
        async with async_session_maker() as db:
            await init_database(db)
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down Enterprise Boilerplate Backend...")
    await close_db()
    await close_redis()
    print("✅ Database and Redis connections closed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Enterprise Boilerplate API",
        description="Enterprise-grade boilerplate application backend",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add test routers
    app.include_router(test_redis_router)

    # Add API v1 router
    app.include_router(api_v1_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {"status": "healthy"}

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": "Enterprise Boilerplate API",
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
        }

    return app


app = create_application()
