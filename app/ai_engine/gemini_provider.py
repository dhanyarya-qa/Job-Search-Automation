"""
Gemini Provider — Async Google Gemini API integration.
"""

from __future__ import annotations

import structlog
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.ai_engine.retry_handler import async_retry
from app.config import settings

logger = structlog.get_logger(__name__)


class GeminiProvider:
    """Async Gemini provider using google-generativeai SDK."""

    PROVIDER_NAME = "gemini"

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=GenerationConfig(
                temperature=0.3,
                top_p=0.95,
                top_k=40,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )
        self._text_model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=4096,
            ),
        )

    @async_retry(max_attempts=3, min_wait=1.0, max_wait=8.0)
    async def complete(self, prompt: str, temperature: float = 0.3) -> tuple[str, int]:
        """
        Generate JSON completion via Gemini.
        Returns (content, tokens_used).
        """
        response = await self._model.generate_content_async(prompt)
        content = response.text or ""
        tokens = (
            response.usage_metadata.total_token_count
            if response.usage_metadata
            else 0
        )
        logger.info("Gemini completion", model=self.model_name, tokens=tokens)
        return content, tokens

    @async_retry(max_attempts=3, min_wait=1.0, max_wait=8.0)
    async def complete_text(self, prompt: str, temperature: float = 0.7) -> tuple[str, int]:
        """Free-text completion via Gemini (no JSON enforcement)."""
        response = await self._text_model.generate_content_async(prompt)
        content = response.text or ""
        tokens = (
            response.usage_metadata.total_token_count
            if response.usage_metadata
            else 0
        )
        return content, tokens

    async def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(settings.gemini_api_key)
