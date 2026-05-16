"""
AI Analysis Repository — Domain queries for AIAnalysis model.
"""

from __future__ import annotations

import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.ai_analysis import AIAnalysis
from app.database.repositories.base_repository import BaseRepository


class AIAnalysisRepository(BaseRepository[AIAnalysis]):
    model_class = AIAnalysis

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_job_id(self, job_id: uuid.UUID) -> AIAnalysis | None:
        """Get the latest AI analysis for a given job."""
        result = await self._session.execute(
            select(AIAnalysis)
            .where(AIAnalysis.job_id == job_id)
            .order_by(desc(AIAnalysis.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_top_matches(self, min_score: float = 70.0, limit: int = 20) -> list[AIAnalysis]:
        """Return top AI matches above a minimum score threshold."""
        result = await self._session.execute(
            select(AIAnalysis)
            .where(AIAnalysis.match_score >= min_score)
            .order_by(desc(AIAnalysis.match_score))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_score_distribution(self) -> dict[str, int]:
        """Return count of jobs per score bucket."""
        analyses = await self.get_all(limit=10000)
        distribution: dict[str, int] = {
            "90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "below-60": 0
        }
        for a in analyses:
            if a.match_score is None:
                continue
            if a.match_score >= 90:
                distribution["90-100"] += 1
            elif a.match_score >= 80:
                distribution["80-89"] += 1
            elif a.match_score >= 70:
                distribution["70-79"] += 1
            elif a.match_score >= 60:
                distribution["60-69"] += 1
            else:
                distribution["below-60"] += 1
        return distribution
