"""
Telegram Notifier — Sends job alerts and AI results via Telegram bot.
"""

from __future__ import annotations

import structlog
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
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

    async def send_message(self, text: str, parse_mode: str = "HTML", reply_markup=None) -> bool:
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
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
            logger.info("Telegram message sent")
            return True
        except TelegramError as e:
            logger.error("Telegram send failed", error=str(e))
            return False

    async def send_job_notification(
        self,
        job_title: str,
        company_name: str,
        location: str,
        salary: str | None,
        job_url: str,
        apply_email: str | None,
        apply_link: str | None,
        platform: str,
        is_priority: bool = False,
    ) -> bool:
        """Send a formatted job notification with inline buttons."""
        
        # Priority emoji
        priority_emoji = "⭐ " if is_priority else ""
        
        # Build message
        text = f"{priority_emoji}🎯 <b>New Job Found!</b>\n\n"
        text += f"📋 <b>{job_title}</b>\n"
        text += f"🏢 {company_name}\n"
        text += f"📍 {location}\n"
        
        if salary:
            text += f"💰 {salary}\n"
        
        text += f"🌐 Platform: {platform.title()}\n\n"
        
        # Add apply information
        text += "<b>📨 How to Apply:</b>\n"
        
        if apply_email:
            text += f"✉️ Email: <code>{apply_email}</code>\n"
        
        if apply_link:
            text += f"🔗 <a href='{apply_link}'>Apply Here</a>\n"
        elif job_url:
            text += f"🔗 <a href='{job_url}'>View Job</a>\n"
        
        # Create inline keyboard buttons
        buttons = []
        
        # Row 1: Apply buttons
        row1 = []
        if apply_link:
            row1.append(InlineKeyboardButton("📝 Apply Now", url=apply_link))
        elif job_url:
            row1.append(InlineKeyboardButton("👀 View Job", url=job_url))
        
        if row1:
            buttons.append(row1)
        
        # Row 2: Action buttons (callback data for future tracking)
        row2 = [
            InlineKeyboardButton("💾 Save", callback_data=f"save_{job_url[:50]}"),
            InlineKeyboardButton("❌ Not Interested", callback_data=f"reject_{job_url[:50]}"),
        ]
        buttons.append(row2)
        
        # Row 3: Company info
        if company_name:
            company_search = company_name.replace(" ", "+")
            row3 = [
                InlineKeyboardButton("🏢 Company Info", url=f"https://www.google.com/search?q={company_search}"),
            ]
            buttons.append(row3)
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        return await self.send_message(text, reply_markup=reply_markup)

    async def notify_new_job(
        self,
        job_title: str,
        company_name: str,
        match_score: float,
        prediction_market: str,
        job_url: str,
    ) -> bool:
        """Send a formatted new job alert (legacy method)."""
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

    async def notify_scrape_complete(self, jobs_found: int, jobs_sent: int, jobs_skipped: int = 0) -> bool:
        """Notify when a scraping run completes."""
        text = (
            f"✅ <b>Scraping Complete</b>\n\n"
            f"🔍 Found: {jobs_found} jobs\n"
            f"🆕 New: {jobs_sent} jobs\n"
            f"⏭️ Skipped: {jobs_skipped} (already sent)"
        )
        return await self.send_message(text)

    async def notify_daily_summary(
        self,
        total_jobs: int,
        new_jobs: int,
        top_companies: list[str],
        top_platforms: dict[str, int],
    ) -> bool:
        """Send daily summary report."""
        text = "📊 <b>Daily Job Report</b>\n\n"
        text += f"📈 Total jobs in database: {total_jobs}\n"
        text += f"🆕 New jobs today: {new_jobs}\n\n"
        
        if top_companies:
            text += "<b>🏢 Top Companies:</b>\n"
            for i, company in enumerate(top_companies[:5], 1):
                text += f"{i}. {company}\n"
            text += "\n"
        
        if top_platforms:
            text += "<b>🌐 Jobs by Platform:</b>\n"
            for platform, count in sorted(top_platforms.items(), key=lambda x: x[1], reverse=True):
                text += f"• {platform.title()}: {count}\n"
        
        return await self.send_message(text)

    async def notify_error(self, module: str, error: str) -> bool:
        """Notify on system errors."""
        text = (
            f"❌ <b>System Error</b>\n\n"
            f"📦 Module: {module}\n"
            f"⚠️ Error: {error[:200]}"
        )
        return await self.send_message(text)

    async def notify_job_expiring(self, job_title: str, company: str, days_left: int, job_url: str) -> bool:
        """Notify about job expiring soon."""
        emoji = "🔥" if days_left <= 2 else "⏰"
        text = (
            f"{emoji} <b>Job Expiring Soon!</b>\n\n"
            f"📋 {job_title}\n"
            f"🏢 {company}\n"
            f"⏳ Expires in: <b>{days_left} days</b>\n\n"
            f"🔗 <a href='{job_url}'>Apply Now</a>"
        )
        
        buttons = [[
            InlineKeyboardButton("📝 Apply Now", url=job_url),
            InlineKeyboardButton("⏰ Remind Later", callback_data=f"remind_{job_url[:50]}"),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        return await self.send_message(text, reply_markup=reply_markup)

