"""
Scraping Log Model — Tracks scraper runs and statistics.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.engine import Base


class ScrapingLog(Base):
    __tablename__ = "scraping_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scraper_type: Mapped[str] = mapped_column(String(50), nullable=False)  # local, web3
    platform: Mapped[str] = mapped_column(String(100), nullable=False)
    keyword: Mapped[str | None] = mapped_column(String(255))
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_saved: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, success, failed
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<ScrapingLog id={self.id} platform={self.platform} status={self.status}>"
