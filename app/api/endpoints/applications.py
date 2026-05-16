"""
Applications Endpoints — Track job application status.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.database.models.application import ApplicationStatus
from app.database.repositories.application_repository import ApplicationRepository
from app.database.session import get_async_session

logger = structlog.get_logger(__name__)
router = APIRouter()


class CreateApplicationRequest(BaseModel):
    job_id: uuid.UUID
    notes: str = ""


class UpdateStatusRequest(BaseModel):
    status: ApplicationStatus


@router.post("/", response_class=ORJSONResponse)
async def create_application(
    body: CreateApplicationRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = ApplicationRepository(session)
    app = await repo.create(job_id=body.job_id, notes=body.notes)
    return {"id": str(app.id), "status": app.status, "created_at": str(app.created_at)}


@router.get("/", response_class=ORJSONResponse)
async def list_applications(
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = ApplicationRepository(session)
    apps = await repo.get_all(limit=100)
    return {
        "count": len(apps),
        "results": [
            {"id": str(a.id), "job_id": str(a.job_id), "status": a.status}
            for a in apps
        ],
    }


@router.patch("/{app_id}/status", response_class=ORJSONResponse)
async def update_status(
    app_id: uuid.UUID,
    body: UpdateStatusRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = ApplicationRepository(session)
    app = await repo.update(app_id, status=body.status)
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return {"id": str(app.id), "status": app.status}
