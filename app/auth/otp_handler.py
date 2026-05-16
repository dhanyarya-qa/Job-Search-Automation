"""
OTP Handler — Time-based OTP generation and verification.
"""

from __future__ import annotations

import hashlib
import random
import string
from datetime import datetime, timedelta, timezone

import structlog
from passlib.context import CryptContext

from app.config import settings

logger = structlog.get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP code."""
    return "".join(random.choices(string.digits, k=length))


def hash_otp(otp: str) -> str:
    """Hash OTP for secure storage using SHA256."""
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify an OTP against its hash."""
    return hashlib.sha256(plain_otp.encode()).hexdigest() == hashed_otp


def get_otp_expiry() -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)


def is_otp_expired(expires_at: datetime) -> bool:
    return datetime.now(tz=timezone.utc) > expires_at
