"""
Base Repository — Generic async CRUD repository pattern.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import Base

logger = structlog.get_logger(__name__)

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing CRUD operations.
    Extend this class for each domain model.
    """

    model_class: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **kwargs: Any) -> ModelT:
        """Create and persist a new record."""
        instance = self.model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        logger.debug("Created record", model=self.model_class.__name__, id=str(instance.id))
        return instance

    async def get_by_id(self, record_id: uuid.UUID) -> ModelT | None:
        """Fetch a single record by its primary key."""
        result = await self._session.execute(
            select(self.model_class).where(self.model_class.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: list[Any] | None = None,
    ) -> list[ModelT]:
        """Fetch paginated records with optional filters."""
        query = select(self.model_class)
        if filters:
            for f in filters:
                query = query.where(f)
        query = query.offset(offset).limit(limit).order_by(self.model_class.created_at.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: list[Any] | None = None) -> int:
        """Count records with optional filters."""
        query = select(func.count()).select_from(self.model_class)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def update(self, record_id: uuid.UUID, **kwargs: Any) -> ModelT | None:
        """Update a record by ID."""
        instance = await self.get_by_id(record_id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        logger.debug("Updated record", model=self.model_class.__name__, id=str(record_id))
        return instance

    async def delete(self, record_id: uuid.UUID) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        instance = await self.get_by_id(record_id)
        if not instance:
            return False
        await self._session.delete(instance)
        await self._session.flush()
        logger.debug("Deleted record", model=self.model_class.__name__, id=str(record_id))
        return True
