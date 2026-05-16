"""
Ultimate Job Hunting ATS — FastAPI Application Entry Point
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from app.api.router import api_router
from app.config import settings
from app.database.engine import create_tables, dispose_engine
from app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    configure_logging()
    logger.info("Starting Ultimate Job Hunting ATS", env=settings.app_env)

    # Initialize database tables
    await create_tables()
    logger.info("Database tables initialized")

    yield

    # Cleanup
    await dispose_engine()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Enterprise AI-powered Job Hunting ATS for Dhany Arya Pratama",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ─── Middleware ───────────────────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not settings.is_production else ["https://your-domain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Routers ──────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ─── Health endpoint ─────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check(request: Request) -> dict:
        return {
            "status": "healthy",
            "app": settings.app_name,
            "env": settings.app_env,
            "version": "1.0.0",
        }

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=not settings.is_production,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
