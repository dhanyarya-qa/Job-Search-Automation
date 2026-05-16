"""
Application Repository — Domain queries for Application tracking.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.application import Application, ApplicationStatus
from app.database.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    model_class = Application

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_status(self, status: ApplicationStatus) -> list[Application]:
        """Fetch applications by status."""
        result = await self._session.execute(
            select(Application)
            .where(Application.status == status)
            .order_by(Application.applied_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_followups(self) -> list[Application]:
        """Return applications with overdue or upcoming follow-ups."""
        from datetime import datetime, timezone  # noqa: PLC0415
        now = datetime.now(tz=timezone.utc)
        result = await self._session.execute(
            select(Application).where(
                Application.followup_due <= now,
                Application.status.notin_(
                    [ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]
                ),
            )
        )
        return list(result.scalars().all())
