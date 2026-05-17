"""Database models package init."""

from app.database.models.ai_analysis import AIAnalysis
from app.database.models.alert import Alert
from app.database.models.application import Application
from app.database.models.application_tracking import ApplicationTracking, ApplicationStatus
from app.database.models.company import Company
from app.database.models.followup import FollowUp
from app.database.models.generated_artifact import GeneratedArtifact
from app.database.models.job import Job
from app.database.models.otp_session import OTPSession
from app.database.models.scraping_log import ScrapingLog

__all__ = [
    "AIAnalysis",
    "Alert",
    "Application",
    "ApplicationTracking",
    "ApplicationStatus",
    "Company",
    "FollowUp",
    "GeneratedArtifact",
    "Job",
    "OTPSession",
    "ScrapingLog",
]
