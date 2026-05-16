"""
Email Notifier — Async SMTP email notifications.
"""

from __future__ import annotations

import structlog
from aiosmtplib import SMTP, SMTPException

from app.config import settings

logger = structlog.get_logger(__name__)


class EmailNotifier:
    """Sends email notifications via async SMTP."""

    def __init__(self) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._user = settings.smtp_user
        self._password = settings.smtp_password
        self._from = settings.email_from

    def _is_configured(self) -> bool:
        return bool(self._user and self._password and self._from)

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """Send an email. Returns True on success."""
        if not self._is_configured():
            logger.warning("Email not configured, skipping")
            return False

        from email.mime.multipart import MIMEMultipart  # noqa: PLC0415
        from email.mime.text import MIMEText  # noqa: PLC0415

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = to

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        try:
            async with SMTP(
                hostname=self._host,
                port=self._port,
                use_tls=False,
                start_tls=True,
            ) as smtp:
                await smtp.login(self._user, self._password)
                await smtp.send_message(msg)
            logger.info("Email sent", to=to, subject=subject)
            return True
        except SMTPException as e:
            logger.error("Email send failed", error=str(e))
            return False

    async def notify_new_high_match(
        self,
        to: str,
        job_title: str,
        company: str,
        score: float,
        job_url: str,
    ) -> bool:
        """Send a high-match job alert email."""
        subject = f"🎯 High Match Found: {job_title} at {company} ({score:.0f}/100)"
        body = f"""
        <html><body>
        <h2>🎯 New High-Match Job Alert</h2>
        <p><strong>Position:</strong> {job_title}</p>
        <p><strong>Company:</strong> {company}</p>
        <p><strong>AI Match Score:</strong> <span style="color:green;font-size:1.4em">{score:.0f}/100</span></p>
        <p><a href="{job_url}" style="background:#667eea;color:white;padding:10px 20px;
        border-radius:8px;text-decoration:none;display:inline-block;margin-top:10px">
        View Job →</a></p>
        <hr/>
        <small>Ultimate Job Hunting ATS — by Dhany Arya Pratama</small>
        </body></html>
        """
        return await self.send(to, subject, body, html=True)
