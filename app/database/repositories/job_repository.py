"""
Job Repository — Domain-specific queries for Job model.
"""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.job import Job
from app.database.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class JobRepository(BaseRepository[Job]):
    model_class = Job

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_url(self, job_url: str) -> Job | None:
        """Fetch a job by its source URL (deduplication)."""
        result = await self._session.execute(
            select(Job).where(Job.job_url == job_url)
        )
        return result.scalar_one_or_none()

    async def exists_by_url(self, job_url: str) -> bool:
        """Check if a job with this URL already exists."""
        return await self.get_by_url(job_url) is not None

    async def get_by_platform(self, platform: str, limit: int = 50) -> list[Job]:
        """Fetch jobs filtered by source platform."""
        result = await self._session.execute(
            select(Job)
            .where(Job.source_platform == platform)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(self, keyword: str, limit: int = 50) -> list[Job]:
        """Full-text search on job title and description."""
        result = await self._session.execute(
            select(Job).where(
                Job.job_title.ilike(f"%{keyword}%") | Job.description.ilike(f"%{keyword}%")
            ).order_by(Job.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_unanalyzed(self, limit: int = 20) -> list[Job]:
        """Return jobs that have no AI analysis yet."""
        from app.database.models.ai_analysis import AIAnalysis  # noqa: PLC0415
        subq = select(AIAnalysis.job_id)
        result = await self._session.execute(
            select(Job).where(Job.id.not_in(subq)).limit(limit)
        )
        return list(result.scalars().all())
