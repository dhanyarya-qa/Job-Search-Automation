"""
Run AI Engine — Process unanalyzed jobs through AI pipeline.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.ai_engine.orchestrator import AIOrchestrator
from app.database.engine import AsyncSessionLocal
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.ai_analysis_repository import AIAnalysisRepository
from app.scraper.output_writer import OutputWriter
from app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


async def main() -> None:
    configure_logging()
    orchestrator = AIOrchestrator()
    writer = OutputWriter()
    results = []

    async with AsyncSessionLocal() as session:
        job_repo = JobRepository(session)
        ai_repo = AIAnalysisRepository(session)

        unanalyzed = await job_repo.get_unanalyzed(limit=50)
        logger.info("Jobs to analyze", count=len(unanalyzed))

        for job in unanalyzed:
            try:
                result = await orchestrator.full_analysis(
                    job_title=job.job_title,
                    company_name=job.company_name,
                    job_description=job.description or "",
                )
                await ai_repo.create(
                    job_id=job.id,
                    match_score=result.match_score,
                    reasoning=result.reasoning,
                    job_category=result.job_category,
                    prediction_market=result.prediction_market,
                    confidence=result.confidence,
                    cover_letter=result.cover_letter,
                    interview_questions=json.dumps(result.interview_questions),
                    ai_provider_used=result.ai_provider_used,
                    tokens_used=result.tokens_used,
                )
                results.append(result.model_dump())
                logger.info("Analyzed job", job=job.job_title, score=result.match_score)
            except Exception as e:
                logger.error("Failed to analyze job", job=job.job_title, error=str(e))

        await session.commit()

    writer.write_ai_results(results, "ai_analysis_results")
    logger.info("AI engine pipeline complete", analyzed=len(results))


if __name__ == "__main__":
    asyncio.run(main())
