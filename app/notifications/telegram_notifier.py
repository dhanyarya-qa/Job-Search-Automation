"""
Telegram Notifier — Sends job alerts and AI results via Telegram bot.
"""

from __future__ import annotations

import structlog
from telegram import Bot
from telegram.error import TelegramError

from app.config import settings

logger = structlog.get_logger(__name__)


class TelegramNotifier:
    """Sends notifications via Telegram Bot API."""

    def __init__(self) -> None:
        self._token = settings.telegram_bot_token
        self._chat_id = settings.telegram_chat_id
        self._bot: Bot | None = None

    def _get_bot(self) -> Bot:
        if not self._bot:
            self._bot = Bot(token=self._token)
        return self._bot

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send a plain text or HTML message."""
        if not self._token or not self._chat_id:
            logger.warning("Telegram not configured, skipping notification")
            return False
        try:
            bot = self._get_bot()
            await bot.send_message(
                chat_id=self._chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info("Telegram message sent")
            return True
        except TelegramError as e:
            logger.error("Telegram send failed", error=str(e))
            return False

    async def notify_new_job(
        self,
        job_title: str,
        company_name: str,
        match_score: float,
        prediction_market: str,
        job_url: str,
    ) -> bool:
        """Send a formatted new job alert."""
        score_emoji = "🚀" if match_score >= 90 else "💪" if match_score >= 75 else "🎯"
        text = (
            f"{score_emoji} <b>New Job Match!</b>\n\n"
            f"📋 <b>{job_title}</b>\n"
            f"🏢 {company_name}\n"
            f"🎯 Match Score: <b>{match_score:.0f}/100</b>\n"
            f"📈 {prediction_market}\n\n"
            f"🔗 <a href='{job_url}'>View Job</a>"
        )
        return await self.send_message(text)

    async def notify_scrape_complete(self, jobs_found: int, jobs_saved: int) -> bool:
        """Notify when a scraping run completes."""
        text = (
            f"✅ <b>Scraping Complete</b>\n\n"
            f"🔍 Found: {jobs_found} jobs\n"
            f"💾 Saved: {jobs_saved} new jobs"
        )
        return await self.send_message(text)

    async def notify_error(self, module: str, error: str) -> bool:
        """Notify on system errors."""
        text = (
            f"❌ <b>System Error</b>\n\n"
            f"📦 Module: {module}\n"
            f"⚠️ Error: {error[:200]}"
        )
        return await self.send_message(text)
