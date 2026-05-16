"""
Cover Letter Engine — Generates hyper-personalized cover letters.
"""

from __future__ import annotations

import structlog

from app.ai_engine.prompt_builder import PromptBuilder
from app.ai_engine.provider_manager import ProviderManager

logger = structlog.get_logger(__name__)


class CoverLetterEngine:
    """Generates personalized cover letters using AI."""

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._pm = provider_manager
        self._prompt_builder = PromptBuilder()

    async def generate(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        match_score: float,
        reasoning: str,
    ) -> tuple[str, str]:
        """
        Generate a cover letter.
        Returns (cover_letter_text, provider_name).
        """
        prompt = self._prompt_builder.build_cover_letter_prompt(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            match_score=match_score,
            reasoning=reasoning,
        )
        content, tokens, provider = await self._pm.complete_text(prompt, temperature=0.7)
        logger.info("Cover letter generated", provider=provider, tokens=tokens, chars=len(content))
        return content.strip(), provider
