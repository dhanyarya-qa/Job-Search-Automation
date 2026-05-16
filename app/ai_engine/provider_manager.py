"""
Provider Manager — Manages AI provider selection and failover.
"""

from __future__ import annotations

import structlog

from app.ai_engine.anthropic_provider import AnthropicProvider
from app.ai_engine.gemini_provider import GeminiProvider
from app.ai_engine.openai_provider import OpenAIProvider
from app.config import settings

logger = structlog.get_logger(__name__)


class ProviderManager:
    """
    Manages multiple AI providers with primary/fallback logic.
    Providers are tried in priority order on failure.
    """

    def __init__(self) -> None:
        self._gemini = GeminiProvider()
        self._openai = OpenAIProvider()
        self._anthropic = AnthropicProvider()

        # Build priority order based on configured primary
        self._providers: dict[str, GeminiProvider | OpenAIProvider | AnthropicProvider] = {
            "gemini": self._gemini,
            "openai": self._openai,
            "anthropic": self._anthropic,
        }

        primary = settings.primary_ai_provider
        others = [k for k in self._providers if k != primary]
        self._priority: list[str] = [primary] + others

    async def complete_json(self, prompt: str, temperature: float = 0.3) -> tuple[str, int, str]:
        """
        Try providers in priority order for JSON completion.
        Returns (content, tokens, provider_name).
        """
        last_error: Exception | None = None
        for name in self._priority:
            provider = self._providers[name]
            try:
                if not await provider.is_available():
                    logger.warning("Provider not configured", provider=name)
                    continue
                content, tokens = await provider.complete(prompt, temperature)
                logger.info("Provider succeeded", provider=name)
                return content, tokens, name
            except Exception as e:
                last_error = e
                logger.warning("Provider failed, trying fallback", provider=name, error=str(e))
        raise RuntimeError(
            f"All AI providers failed. Last error: {last_error}"
        )

    async def complete_text(self, prompt: str, temperature: float = 0.7) -> tuple[str, int, str]:
        """
        Try providers in priority order for free-text completion.
        Returns (content, tokens, provider_name).
        """
        last_error: Exception | None = None
        for name in self._priority:
            provider = self._providers[name]
            try:
                if not await provider.is_available():
                    continue
                content, tokens = await provider.complete_text(prompt, temperature)
                return content, tokens, name
            except Exception as e:
                last_error = e
                logger.warning("Text provider failed, trying fallback", provider=name, error=str(e))
        raise RuntimeError(f"All AI providers failed for text completion. Last: {last_error}")

    def get_primary_provider_name(self) -> str:
        return self._priority[0]
