"""
API Router — Registers all endpoint routers.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints import ai_analysis, alerts, applications, auth, health, jobs

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(ai_analysis.router, prefix="/ai-analysis", tags=["AI Analysis"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
