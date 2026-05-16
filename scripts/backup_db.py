"""
DB Backup Script — Exports jobs and AI analysis to CSV/JSON snapshots.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.database.engine import AsyncSessionLocal
from app.database.repositories.ai_analysis_repository import AIAnalysisRepository
from app.database.repositories.job_repository import JobRepository
from app.scraper.output_writer import OutputWriter
from app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


async def backup() -> None:
    configure_logging()
    writer = OutputWriter()
    today = datetime.now(tz=timezone.utc).strftime("%Y%m%d")

    async with AsyncSessionLocal() as session:
        job_repo = JobRepository(session)
        ai_repo = AIAnalysisRepository(session)

        # Backup jobs
        jobs = await job_repo.get_all(limit=100_000)
        job_dicts = [
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
        ]

        writer.write_jobs_json(job_dicts, f"backup_jobs_{today}")
        writer.write_jobs_csv(job_dicts, f"backup_jobs_{today}")
        logger.info("Jobs backed up", count=len(job_dicts))

        # Backup AI analysis
        analyses = await ai_repo.get_all(limit=100_000)
        ai_dicts = [
            {
                "id": str(a.id),
                "job_id": str(a.job_id),
                "match_score": a.match_score,
                "job_category": a.job_category,
                "prediction_market": a.prediction_market,
                "ai_provider_used": a.ai_provider_used,
                "created_at": str(a.created_at),
            }
            for a in analyses
        ]

        writer.write_jobs_json(ai_dicts, f"backup_ai_analysis_{today}")
        writer.write_jobs_csv(ai_dicts, f"backup_ai_analysis_{today}")
        logger.info("AI analysis backed up", count=len(ai_dicts))

    logger.info("Backup complete", date=today)


if __name__ == "__main__":
    asyncio.run(backup())
