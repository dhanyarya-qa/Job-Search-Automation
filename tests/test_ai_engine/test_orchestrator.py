"""Tests for scoring engine."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai_engine.orchestrator import AIOrchestrator
from app.ai_engine.response_parser import MatchScoreResult


@pytest.mark.asyncio
async def test_quick_score_returns_float() -> None:
    mock_result = MatchScoreResult(
        match_score=88.0,
        reasoning="Strong match for QA Automation role",
        job_category="Automation",
        confidence=0.88,
        prediction_market="Bullish — 💪 Strong Match (80% Win Rate)",
    )
    with patch.object(
        AIOrchestrator, "full_analysis", new_callable=AsyncMock, return_value=mock_result
    ):
        orchestrator = AIOrchestrator()
        with patch.object(orchestrator._scoring_engine, "score_job", new_callable=AsyncMock, return_value=mock_result):
            score = await orchestrator.quick_score(
                job_title="QA Engineer",
                company_name="Tech Corp",
                job_description="We need a QA automation engineer with Playwright experience.",
            )
    assert isinstance(score, float)
    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_prompt_builder_contains_candidate_name() -> None:
    from app.ai_engine.prompt_builder import PromptBuilder  # noqa: PLC0415
    from app.ai_engine.ai_constants import CANDIDATE_NAME  # noqa: PLC0415

    prompt = PromptBuilder.build_match_scoring_prompt(
        job_title="QA Automation",
        company_name="Acme",
        job_description="Need QA engineer with Playwright skills",
    )
    assert CANDIDATE_NAME in prompt
    assert "match_score" in prompt
