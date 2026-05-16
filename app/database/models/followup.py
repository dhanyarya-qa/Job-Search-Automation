"""
FollowUp Model — Follow-up tracking per application.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    follow_up_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="email")  # email, linkedin, phone
    notes: Mapped[str | None] = mapped_column(Text)
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    application: Mapped["Application"] = relationship(  # noqa: F821
        "Application", back_populates="followups"
    )

    def __repr__(self) -> str:
        return f"<FollowUp id={self.id} app_id={self.application_id} due={self.follow_up_date}>"
