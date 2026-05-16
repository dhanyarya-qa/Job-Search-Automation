"""
AI Analysis Endpoints — Trigger and retrieve AI analysis for jobs.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_engine.orchestrator import AIOrchestrator
from app.auth.security import get_current_user
from app.database.repositories.ai_analysis_repository import AIAnalysisRepository
from app.database.repositories.job_repository import JobRepository
from app.database.session import get_async_session

logger = structlog.get_logger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    job_id: uuid.UUID
    generate_cover_letter: bool = True
    generate_interview_prep: bool = True


@router.post("/analyze", response_class=ORJSONResponse)
async def analyze_job(
    body: AnalyzeRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    """Run full AI analysis for a specific job."""
    job_repo = JobRepository(session)
    job = await job_repo.get_by_id(body.job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    orchestrator = AIOrchestrator()
    result = await orchestrator.full_analysis(
        job_title=job.job_title,
        company_name=job.company_name,
        job_description=job.description or "",
        generate_cover_letter=body.generate_cover_letter,
        generate_interview_prep=body.generate_interview_prep,
    )

    # Persist
    ai_repo = AIAnalysisRepository(session)
    analysis = await ai_repo.create(
        job_id=job.id,
        match_score=result.match_score,
        reasoning=result.reasoning,
        job_category=result.job_category,
        prediction_market=result.prediction_market,
        confidence=result.confidence,
        cover_letter=result.cover_letter,
        interview_questions=str(result.interview_questions),
        ai_provider_used=result.ai_provider_used,
        tokens_used=result.tokens_used,
    )

    return {
        "analysis_id": str(analysis.id),
        "match_score": result.match_score,
        "reasoning": result.reasoning,
        "job_category": result.job_category,
        "prediction_market": result.prediction_market,
        "confidence": result.confidence,
        "cover_letter": result.cover_letter,
        "interview_questions": result.interview_questions,
    }


@router.get("/top-matches", response_class=ORJSONResponse)
async def top_matches(
    min_score: float = 70.0,
    limit: int = 20,
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = AIAnalysisRepository(session)
    matches = await repo.get_top_matches(min_score=min_score, limit=limit)
    return {
        "count": len(matches),
        "min_score": min_score,
        "results": [
            {
                "id": str(m.id),
                "job_id": str(m.job_id),
                "match_score": m.match_score,
                "job_category": m.job_category,
                "prediction_market": m.prediction_market,
            }
            for m in matches
        ],
    }


@router.get("/score-distribution", response_class=ORJSONResponse)
async def score_distribution(
    session: AsyncSession = Depends(get_async_session),
    _current_user: dict = Depends(get_current_user),
) -> dict:
    repo = AIAnalysisRepository(session)
    distribution = await repo.get_score_distribution()
    return {"distribution": distribution}
