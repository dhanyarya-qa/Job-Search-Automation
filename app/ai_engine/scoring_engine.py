"""
Scoring Engine — Generates AI match scores for jobs.
"""

from __future__ import annotations

import json

import structlog

from app.ai_engine.ai_constants import get_prediction_label
from app.ai_engine.prompt_builder import PromptBuilder
from app.ai_engine.provider_manager import ProviderManager
from app.ai_engine.response_parser import MatchScoreResult

logger = structlog.get_logger(__name__)


class ScoringEngine:
    """Computes match scores between candidate and job listings using AI."""

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._pm = provider_manager
        self._prompt_builder = PromptBuilder()

    async def score_job(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        tech_stack: list[str] | None = None,
    ) -> MatchScoreResult:
        """
        Generate a complete AI scoring analysis for a job.
        Returns a validated MatchScoreResult.
        """
        prompt = self._prompt_builder.build_match_scoring_prompt(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            tech_stack=tech_stack,
        )

        content, tokens, provider = await self._pm.complete_json(prompt)
        logger.info("Scoring complete", provider=provider, tokens=tokens)

        try:
            raw = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI scoring response", error=str(e), content=content[:200])
            raise ValueError(f"AI returned invalid JSON: {e}") from e

        # Ensure prediction_market is computed
        score = float(raw.get("match_score", 0))
        raw.setdefault("prediction_market", get_prediction_label(score))
        raw.setdefault("confidence", min(score / 100.0, 1.0))
        raw["ai_provider_used"] = provider
        raw["tokens_used"] = tokens

        return MatchScoreResult(**raw)
