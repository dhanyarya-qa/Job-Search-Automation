"""
Alert Repository — Domain queries for Alert model.
"""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.alert import Alert
from app.database.repositories.base_repository import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    model_class = Alert

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_unread(self, limit: int = 50) -> list[Alert]:
        """Fetch unread alerts."""
        result = await self._session.execute(
            select(Alert)
            .where(Alert.is_read == False)  # noqa: E712
            .order_by(Alert.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_all_read(self) -> int:
        """Mark all alerts as read. Returns count updated."""
        result = await self._session.execute(
            update(Alert).where(Alert.is_read == False).values(is_read=True)  # noqa: E712
        )
        return result.rowcount
