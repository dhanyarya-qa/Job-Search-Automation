"""
AI Analysis Model — Stores AI engine output for each job.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, CHAR

from app.database.engine import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            return str(value) if isinstance(value, uuid.UUID) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
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
