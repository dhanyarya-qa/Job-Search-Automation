"""
Interview Engine — Generates predicted interview questions and model answers.
"""

from __future__ import annotations

import json

import structlog

from app.ai_engine.prompt_builder import PromptBuilder
from app.ai_engine.provider_manager import ProviderManager

logger = structlog.get_logger(__name__)


class InterviewEngine:
    """Predicts interview questions with model answers using AI."""

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._pm = provider_manager
        self._prompt_builder = PromptBuilder()

    async def generate_questions(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
    ) -> list[dict[str, str]]:
        """
        Generate interview Q&A pairs.
        Returns list of {question, type, model_answer}.
        """
        prompt = self._prompt_builder.build_interview_prep_prompt(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
        )
        content, tokens, provider = await self._pm.complete_json(prompt)
        logger.info("Interview prep generated", provider=provider, tokens=tokens)

        try:
            data = json.loads(content)
            return data.get("questions", [])
        except json.JSONDecodeError as e:
            logger.error("Failed to parse interview questions", error=str(e))
            return []
