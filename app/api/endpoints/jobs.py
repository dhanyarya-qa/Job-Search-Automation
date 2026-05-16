"""
Jobs Endpoints — CRUD and search for job listings.
"""

from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.database.repositories.job_repository import JobRepository
from app.database.session import get_async_session

logger = structlog.get_logger(__name__)
router = APIRouter()


class JobResponse(BaseModel):
    id: uuid.UUID
    job_title: str
    company_name: str
    location: str | None
    salary: str | None
    source_platform: str
    job_url: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_class=ORJSONResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    platform: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = JobRepository(session)
    offset = (page - 1) * page_size

    if keyword:
        jobs = await repo.search(keyword, limit=page_size)
    elif platform:
        jobs = await repo.get_by_platform(platform, limit=page_size)
    else:
        jobs = await repo.get_all(offset=offset, limit=page_size)

    total = await repo.count()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "id": str(j.id),
                "job_title": j.job_title,
                "company_name": j.company_name,
                "location": j.location,
                "salary": j.salary,
                "source_platform": j.source_platform,
                "job_url": j.job_url,
                "created_at": str(j.created_at),
            }
            for j in jobs
        ],
    }


@router.get("/{job_id}", response_class=ORJSONResponse)
async def get_job(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {
        "id": str(job.id),
        "job_title": job.job_title,
        "company_name": job.company_name,
        "location": job.location,
        "salary": job.salary,
        "description": job.description,
        "source_platform": job.source_platform,
        "job_url": job.job_url,
        "created_at": str(job.created_at),
    }
