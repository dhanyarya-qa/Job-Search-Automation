"""
Alembic env.py — Async migration environment setup.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Check if we're using sync SQLite (for migrations)
db_url = os.environ.get('DATABASE_URL', '')
is_sync_sqlite = db_url.startswith('sqlite:///')

if is_sync_sqlite:
    # For sync SQLite migrations, don't import app modules
    # Import Base and models directly without triggering async engine creation
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(DeclarativeBase):
        """Base class for all SQLAlchemy ORM models."""
        pass
    
    # Import models after Base is defined
    from app.database.models import (  # noqa: F401
        alert, ai_analysis, application, company,
        followup, generated_artifact, job, otp_session, scraping_log,
    )
else:
    # For async databases, use normal imports
    from app.config import settings
    from app.database.engine import Base
    
    # Import all models so Alembic can detect them
    from app.database.models import (  # noqa: F401
        alert, ai_analysis, application, company,
        followup, generated_artifact, job, otp_session, scraping_log,
    )
    
    db_url = settings.database_url

config = context.config
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:  # type: ignore[no-untyped-def]
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    if is_sync_sqlite:
        # Should not reach here for sync SQLite
        raise RuntimeError("Cannot run async migrations with sync SQLite")
    engine = create_async_engine(db_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    # Check if using SQLite (sync) or PostgreSQL (async)
    
    if is_sync_sqlite:
        # Use sync engine for SQLite
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
        engine.dispose()
    else:
        # Use async engine for PostgreSQL
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
