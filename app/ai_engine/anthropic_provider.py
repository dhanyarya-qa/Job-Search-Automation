"""
Anthropic Provider — Async Anthropic Claude API integration.
"""

from __future__ import annotations

import structlog
from anthropic import AsyncAnthropic

from app.ai_engine.ai_constants import REQUEST_TIMEOUT
from app.ai_engine.retry_handler import async_retry
from app.config import settings

logger = structlog.get_logger(__name__)


class AnthropicProvider:
    """Async Anthropic provider for Claude completions."""

    PROVIDER_NAME = "anthropic"

    def __init__(self) -> None:
        self._client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=REQUEST_TIMEOUT,
        )
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens

    @async_retry(max_attempts=3, min_wait=1.0, max_wait=8.0)
    async def complete(self, prompt: str, temperature: float = 0.3) -> tuple[str, int]:
        """
        Generate a message completion via Claude.
        Returns (content, tokens_used).
        """
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text if response.content else ""
        tokens = (
            response.usage.input_tokens + response.usage.output_tokens
            if response.usage
            else 0
        )
        logger.info("Anthropic completion", model=self.model, tokens=tokens)
        return content, tokens

    async def complete_text(self, prompt: str, temperature: float = 0.7) -> tuple[str, int]:
        """Free-text (cover letter, etc.) completion without JSON enforcement."""
        return await self.complete(prompt, temperature=temperature)

    async def is_available(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(settings.anthropic_api_key)
