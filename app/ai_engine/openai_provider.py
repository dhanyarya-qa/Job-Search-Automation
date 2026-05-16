"""
OpenAI Provider — Async OpenAI API integration.
"""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI

from app.ai_engine.ai_constants import MAX_RETRIES, REQUEST_TIMEOUT
from app.ai_engine.retry_handler import async_retry
from app.config import settings

logger = structlog.get_logger(__name__)


class OpenAIProvider:
    """Async OpenAI provider for chat completions."""

    PROVIDER_NAME = "openai"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=REQUEST_TIMEOUT,
            max_retries=MAX_RETRIES,
        )
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

    @async_retry(max_attempts=3, min_wait=1.0, max_wait=8.0)
    async def complete(self, prompt: str, temperature: float = 0.3) -> tuple[str, int]:
        """
        Generate a chat completion.
        Returns (content, tokens_used).
        """
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        logger.info("OpenAI completion", model=self.model, tokens=tokens)
        return content, tokens

    async def complete_text(self, prompt: str, temperature: float = 0.7) -> tuple[str, int]:
        """Generate free-text completion (no JSON enforcement)."""
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=self.max_tokens,
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return content, tokens

    async def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(settings.openai_api_key)
