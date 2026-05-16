"""
Database Engine — Async SQLAlchemy engine and session factory.
"""

from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = structlog.get_logger(__name__)

# ─── Engine ──────────────────────────────────────────────────────
# SQLite doesn't support pool_size and max_overflow
engine_kwargs = {
    "echo": settings.debug,
}

# Only add pool settings for non-SQLite databases
if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

# ─── Session Factory ──────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ─── Base Model ───────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def create_tables() -> None:
    """Create all database tables."""
    from app.database.models import (  # noqa: F401
        alert, ai_analysis, application, company,
        followup, generated_artifact, job, otp_session, scraping_log,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    logger.info("Database tables created")


async def dispose_engine() -> None:
    """Dispose the database engine on shutdown."""
    await engine.dispose()
    logger.info("Database engine disposed")
