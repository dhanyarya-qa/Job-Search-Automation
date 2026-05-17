"""
Job Model — SQLAlchemy ORM model for job listings.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
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


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    job_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    salary: Mapped[str | None] = mapped_column(String(255))
    source_platform: Mapped[str] = mapped_column(String(100), nullable=False)
    job_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    apply_link: Mapped[str | None] = mapped_column(String(2048))  # Direct apply link
    apply_email: Mapped[str | None] = mapped_column(String(255))  # Contact email
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # Job expiry date
    tags: Mapped[str | None] = mapped_column(Text)  # JSON array stored as text
    requirements: Mapped[str | None] = mapped_column(Text)  # JSON array
    tech_stack: Mapped[str | None] = mapped_column(Text)  # JSON array
    job_category_prediction: Mapped[str | None] = mapped_column(String(100))
    job_type: Mapped[str | None] = mapped_column(String(50))  # Full-time, Contract, etc
    experience_level: Mapped[str | None] = mapped_column(String(50))  # Junior, Mid, Senior
    is_remote: Mapped[bool] = mapped_column(default=False)
    is_priority: Mapped[bool] = mapped_column(default=False)  # Priority company
    is_active: Mapped[bool] = mapped_column(default=True)
    sent_to_telegram: Mapped[bool] = mapped_column(default=False)  # Track if sent
    telegram_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ─── Relationships ────────────────────────────────────────────
    ai_analyses: Mapped[list["AIAnalysis"]] = relationship(  # noqa: F821
        "AIAnalysis", back_populates="job", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        "Application", back_populates="job", cascade="all, delete-orphan"
    )
    application_tracking: Mapped[list["ApplicationTracking"]] = relationship(  # noqa: F821
        "ApplicationTracking", back_populates="job", cascade="all, delete-orphan"
    )

    # ─── Indexes ──────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_jobs_company_title", "company_name", "job_title"),
        Index("ix_jobs_platform_date", "source_platform", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.job_title!r} company={self.company_name!r}>"
