"""
FastAPI Dependencies — Dependency injection for repositories and services.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_engine.orchestrator import AIOrchestrator
from app.database.repositories.ai_analysis_repository import AIAnalysisRepository
from app.database.repositories.alert_repository import AlertRepository
from app.database.repositories.application_repository import ApplicationRepository
from app.database.repositories.job_repository import JobRepository
from app.database.session import get_async_session
from app.notifications.telegram_notifier import TelegramNotifier

# ─── Session Dependency ───────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# ─── Repository Dependencies ──────────────────────────────────────
def get_job_repository(session: DBSession) -> JobRepository:
    return JobRepository(session)


def get_ai_analysis_repository(session: DBSession) -> AIAnalysisRepository:
    return AIAnalysisRepository(session)


def get_application_repository(session: DBSession) -> ApplicationRepository:
    return ApplicationRepository(session)


def get_alert_repository(session: DBSession) -> AlertRepository:
    return AlertRepository(session)


# ─── Service Dependencies ──────────────────────────────────────────
def get_ai_orchestrator() -> AIOrchestrator:
    return AIOrchestrator()


def get_telegram_notifier() -> TelegramNotifier:
    return TelegramNotifier()


# ─── Annotated Convenience Types ──────────────────────────────────
JobRepo = Annotated[JobRepository, Depends(get_job_repository)]
AIAnalysisRepo = Annotated[AIAnalysisRepository, Depends(get_ai_analysis_repository)]
ApplicationRepo = Annotated[ApplicationRepository, Depends(get_application_repository)]
AlertRepo = Annotated[AlertRepository, Depends(get_alert_repository)]
AIEngine = Annotated[AIOrchestrator, Depends(get_ai_orchestrator)]
TelegramBot = Annotated[TelegramNotifier, Depends(get_telegram_notifier)]
