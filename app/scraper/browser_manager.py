"""
Browser Manager — Async Playwright browser lifecycle management.
"""

from __future__ import annotations

import structlog
from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

from app.config import settings
from app.scraper.constants import DEFAULT_LOCALE, DEFAULT_TIMEZONE
from app.scraper.proxy_manager import ProxyManager
from app.scraper.stealth_manager import StealthManager

logger = structlog.get_logger(__name__)


class BrowserManager:
    """
    Manages Playwright browser instances with stealth, proxy, and UA rotation.
    Supports context-level isolation for concurrent scraping.
    """

    def __init__(self, proxy_manager: ProxyManager | None = None) -> None:
        self._proxy_manager = proxy_manager or ProxyManager()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Launch the Playwright browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.scraper_headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1366,768",
            ],
        )
        logger.info("Browser started", headless=settings.scraper_headless)

    async def create_context(self) -> BrowserContext:
        """
        Create an isolated browser context with stealth settings.
        Each context gets a fresh user agent, viewport, and optional proxy.
        """
        if not self._browser:
            await self.start()

        proxy = await self._proxy_manager.get_proxy()
        user_agent = StealthManager.get_random_user_agent()
        viewport = StealthManager.get_random_viewport()

        context = await self._browser.new_context(  # type: ignore[union-attr]
            user_agent=user_agent,
            viewport=viewport,
            locale=DEFAULT_LOCALE,
            timezone_id=DEFAULT_TIMEZONE,
            proxy=proxy,
            ignore_https_errors=True,
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
            },
        )

        await StealthManager.apply_stealth(context)
        logger.debug("Browser context created", viewport=viewport, ua=user_agent[:40])
        return context

    async def close(self) -> None:
        """Close browser and Playwright instance."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed")
