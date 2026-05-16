"""
Alerts Endpoints — Manage and retrieve job alerts.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.database.repositories.alert_repository import AlertRepository
from app.database.session import get_async_session

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_class=ORJSONResponse)
async def list_alerts(
    unread_only: bool = False,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = AlertRepository(session)
    alerts = await repo.get_unread() if unread_only else await repo.get_all(limit=50)
    return {
        "count": len(alerts),
        "results": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "title": a.title,
                "message": a.message,
                "is_read": a.is_read,
                "created_at": str(a.created_at),
            }
            for a in alerts
        ],
    }


@router.post("/mark-all-read", response_class=ORJSONResponse)
async def mark_all_read(
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = AlertRepository(session)
    count = await repo.mark_all_read()
    return {"marked_read": count}
