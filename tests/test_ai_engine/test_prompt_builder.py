"""
AI Engine tests — prompt builder, constants, scoring.
"""

from __future__ import annotations

import pytest

from app.ai_engine.ai_constants import (
    CANDIDATE_NAME,
    CANDIDATE_SKILLS,
    JOB_SEARCH_KEYWORDS,
    SCORE_EXCELLENT,
    get_prediction_label,
)
from app.ai_engine.prompt_builder import PromptBuilder


def test_candidate_name_set() -> None:
    assert CANDIDATE_NAME == "Dhany Arya Pratama"


def test_candidate_skills_not_empty() -> None:
    assert len(CANDIDATE_SKILLS) > 5
    assert "Playwright" in CANDIDATE_SKILLS


def test_job_keywords_defined() -> None:
    assert "QA Automation" in JOB_SEARCH_KEYWORDS
    assert "Prompt Engineer" in JOB_SEARCH_KEYWORDS


def test_score_excellent_threshold() -> None:
    assert SCORE_EXCELLENT == 90


def test_prediction_label_bullish() -> None:
    label = get_prediction_label(92)
    assert "Bullish" in label
    assert "Elite" in label


def test_prediction_label_neutral() -> None:
    label = get_prediction_label(65)
    assert "Neutral" in label or "Moderate" in label


def test_prediction_label_bearish() -> None:
    label = get_prediction_label(30)
    assert "Bearish" in label


def test_prompt_contains_json_keys() -> None:
    prompt = PromptBuilder.build_match_scoring_prompt(
        job_title="QA Engineer",
        company_name="Acme Corp",
        job_description="Need QA automation engineer with Playwright.",
    )
    assert "match_score" in prompt
    assert "reasoning" in prompt
    assert "job_category" in prompt
    assert "prediction_market" in prompt
    assert CANDIDATE_NAME in prompt


def test_cover_letter_prompt_structure() -> None:
    prompt = PromptBuilder.build_cover_letter_prompt(
        job_title="SDET",
        company_name="TechCo",
        job_description="Need senior SDET.",
        match_score=88.0,
        reasoning="Strong QA background",
    )
    assert CANDIDATE_NAME in prompt
    assert "cover letter" in prompt.lower()
    assert "350" in prompt  # word limit


def test_interview_prompt_question_types() -> None:
    prompt = PromptBuilder.build_interview_prep_prompt(
        job_title="QA Automation",
        company_name="BigCorp",
        job_description="Automation testing role.",
    )
    assert "technical" in prompt.lower()
    assert "behavioral" in prompt.lower()
    assert "STAR" in prompt
