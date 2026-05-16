"""
AI Response Models — Pydantic schemas for AI engine output.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MatchScoreResult(BaseModel):
    match_score: float = Field(ge=0, le=100, description="Compatibility score 0-100")
    reasoning: str = Field(description="Detailed reasoning for the score")
    job_category: str = Field(description="Category of the job (e.g., Automation, Manual, AI)")
    confidence: float = Field(ge=0, le=1, description="AI confidence level 0-1")
    prediction_market: str = Field(description="Bullish/Neutral/Bearish prediction label")
    cover_letter: str = Field(default="", description="Hyper-personalized cover letter")
    interview_questions: list[str] = Field(
        default_factory=list, description="Predicted interview questions"
    )
    portfolio_suggestions: list[str] = Field(
        default_factory=list, description="Portfolio improvement suggestions"
    )
    ai_provider_used: str = Field(default="", description="Which AI provider generated this")
    tokens_used: int = Field(default=0, description="Tokens consumed")
