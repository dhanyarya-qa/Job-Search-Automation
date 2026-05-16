"""
Session Manager — Manages browser cookie/session persistence.
"""

from __future__ import annotations

import json
from pathlib import Path

import structlog
from playwright.async_api import BrowserContext

logger = structlog.get_logger(__name__)

SESSIONS_DIR = Path("./outputs/sessions")


class SessionManager:
    """
    Persists and restores browser cookies/session state per platform.
    Enables session reuse across scraper runs to avoid repeated logins.
    """

    def __init__(self) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def _session_path(self, platform: str) -> Path:
        return SESSIONS_DIR / f"{platform}_session.json"

    async def save_session(self, context: BrowserContext, platform: str) -> None:
        """Save browser cookies for a platform."""
        try:
            cookies = await context.cookies()
            session_path = self._session_path(platform)
            session_path.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
            logger.info("Session saved", platform=platform, cookies=len(cookies))
        except Exception as e:
            logger.error("Failed to save session", platform=platform, error=str(e))

    async def restore_session(self, context: BrowserContext, platform: str) -> bool:
        """Restore previously saved cookies into a browser context."""
        session_path = self._session_path(platform)
        if not session_path.exists():
            logger.debug("No saved session found", platform=platform)
            return False
        try:
            cookies = json.loads(session_path.read_text(encoding="utf-8"))
            await context.add_cookies(cookies)
            logger.info("Session restored", platform=platform, cookies=len(cookies))
            return True
        except Exception as e:
            logger.error("Failed to restore session", platform=platform, error=str(e))
            return False

    def clear_session(self, platform: str) -> None:
        """Remove saved session for a platform."""
        session_path = self._session_path(platform)
        if session_path.exists():
            session_path.unlink()
            logger.info("Session cleared", platform=platform)

    def has_session(self, platform: str) -> bool:
        return self._session_path(platform).exists()
