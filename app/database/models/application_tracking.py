"""
Application Tracking Model - Track job application status
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class ApplicationStatus(str, Enum):
    """Application status enum"""
    SAVED = "saved"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ApplicationTracking(Base):
    """Track job application progress"""
    __tablename__ = "application_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default=ApplicationStatus.SAVED.value, nullable=False)
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Application details
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    application_method: Mapped[str | None] = mapped_column(String(100), nullable=True)  # email, website, linkedin
    cover_letter_sent: Mapped[bool] = mapped_column(default=False)
    
    # Interview tracking
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # phone, video, onsite
    interview_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Offer tracking
    offer_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    offer_amount: Mapped[str | None] = mapped_column(String(100), nullable=True)
    offer_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Rejection tracking
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationship
    job: Mapped["Job"] = relationship("Job", back_populates="application_tracking")

    def __repr__(self) -> str:
        return f"<ApplicationTracking(id={self.id}, job_id={self.job_id}, status={self.status})>"
