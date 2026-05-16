"""
AI Analysis Model — Stores AI engine output for each job.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    match_score: Mapped[float | None] = mapped_column(Float, index=True)
    reasoning: Mapped[str | None] = mapped_column(Text)
    job_category: Mapped[str | None] = mapped_column(String(100))
    prediction_market: Mapped[str | None] = mapped_column(String(255))
    confidence: Mapped[float | None] = mapped_column(Float)
    cover_letter: Mapped[str | None] = mapped_column(Text)
    interview_questions: Mapped[str | None] = mapped_column(Text)  # JSON array
    portfolio_suggestions: Mapped[str | None] = mapped_column(Text)  # JSON
    ai_provider_used: Mapped[str | None] = mapped_column(String(50))
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # ─── Relationships ────────────────────────────────────────────
    job: Mapped["Job"] = relationship("Job", back_populates="ai_analyses")  # noqa: F821

    __table_args__ = (
        Index("ix_ai_analysis_match_score", "match_score"),
        Index("ix_ai_analysis_job_created", "job_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AIAnalysis id={self.id} job_id={self.job_id} score={self.match_score}>"
