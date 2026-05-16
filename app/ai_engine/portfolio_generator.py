"""
Portfolio Generator — Suggests portfolio projects based on target jobs.
"""

from __future__ import annotations

import json

import structlog

from app.ai_engine.prompt_builder import PromptBuilder
from app.ai_engine.provider_manager import ProviderManager

logger = structlog.get_logger(__name__)


class PortfolioGenerator:
    """Suggests targeted portfolio projects using AI."""

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._pm = provider_manager
        self._prompt_builder = PromptBuilder()

    async def suggest_projects(
        self,
        job_title: str,
        company_name: str,
        tech_stack: list[str],
    ) -> list[dict]:
        """
        Suggest portfolio projects tailored to target company.
        Returns list of project suggestions.
        """
        prompt = self._prompt_builder.build_portfolio_prompt(
            job_title=job_title,
            company_name=company_name,
            tech_stack=tech_stack,
        )
        content, tokens, provider = await self._pm.complete_json(prompt)
        logger.info("Portfolio suggestions generated", provider=provider, tokens=tokens)

        try:
            data = json.loads(content)
            return data.get("portfolio_projects", [])
        except json.JSONDecodeError as e:
            logger.error("Failed to parse portfolio suggestions", error=str(e))
            return []
