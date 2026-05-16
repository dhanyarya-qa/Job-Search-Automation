"""
AI Orchestrator — Central coordinator for all AI engine tasks.
"""

from __future__ import annotations

import json

import structlog

from app.ai_engine.cover_letter_engine import CoverLetterEngine
from app.ai_engine.interview_engine import InterviewEngine
from app.ai_engine.portfolio_generator import PortfolioGenerator
from app.ai_engine.provider_manager import ProviderManager
from app.ai_engine.response_parser import MatchScoreResult
from app.ai_engine.scoring_engine import ScoringEngine

logger = structlog.get_logger(__name__)


class AIOrchestrator:
    """
    Central orchestrator for all AI tasks.
    Coordinates scoring, cover letters, interview prep, and portfolio generation.
    """

    def __init__(self) -> None:
        self._provider_manager = ProviderManager()
        self._scoring_engine = ScoringEngine(self._provider_manager)
        self._cover_letter_engine = CoverLetterEngine(self._provider_manager)
        self._interview_engine = InterviewEngine(self._provider_manager)
        self._portfolio_generator = PortfolioGenerator(self._provider_manager)

    async def full_analysis(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        tech_stack: list[str] | None = None,
        generate_cover_letter: bool = True,
        generate_interview_prep: bool = True,
        generate_portfolio: bool = False,
    ) -> MatchScoreResult:
        """
        Run full AI pipeline for a job:
        1. Match scoring
        2. Cover letter generation
        3. Interview questions (optional)
        4. Portfolio suggestions (optional)
        """
        logger.info(
            "Starting full AI analysis",
            job=job_title,
            company=company_name,
        )

        # Step 1: Score
        result = await self._scoring_engine.score_job(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            tech_stack=tech_stack,
        )
        logger.info("Scored job", score=result.match_score, category=result.job_category)

        # Step 2: Cover letter
        if generate_cover_letter and result.match_score >= 60:
            cover_letter, _ = await self._cover_letter_engine.generate(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                match_score=result.match_score,
                reasoning=result.reasoning,
            )
            result.cover_letter = cover_letter

        # Step 3: Interview prep
        if generate_interview_prep and result.match_score >= 65:
            questions = await self._interview_engine.generate_questions(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
            )
            result.interview_questions = [
                q.get("question", "") for q in questions if q.get("question")
            ]

        # Step 4: Portfolio
        if generate_portfolio and tech_stack:
            suggestions = await self._portfolio_generator.suggest_projects(
                job_title=job_title,
                company_name=company_name,
                tech_stack=tech_stack,
            )
            result.portfolio_suggestions = [
                s.get("title", "") for s in suggestions if s.get("title")
            ]

        logger.info(
            "Full AI analysis complete",
            score=result.match_score,
            prediction=result.prediction_market,
        )
        return result

    async def quick_score(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
    ) -> float:
        """Quick scoring only — no cover letter or interview prep."""
        result = await self._scoring_engine.score_job(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
        )
        return result.match_score
