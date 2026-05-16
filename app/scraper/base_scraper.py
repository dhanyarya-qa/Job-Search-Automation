"""
Base Scraper — Abstract base class for all scrapers.
"""

from __future__ import annotations

import asyncio
import random
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

import structlog
from playwright.async_api import BrowserContext, Page, TimeoutError as PWTimeout

from app.config import settings
from app.scraper.browser_manager import BrowserManager
from app.scraper.captcha_handler import CaptchaHandler
from app.scraper.proxy_manager import ProxyManager
from app.scraper.rate_limiter import RateLimiter
from app.scraper.stealth_manager import StealthManager

logger = structlog.get_logger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class providing:
    - browser initialization and cleanup
    - rate limiting
    - retry with backoff
    - captcha handling
    - stealth behavior
    - debug artifact saving
    """

    SCRAPER_NAME: str = "base"

    def __init__(self) -> None:
        self._proxy_manager = ProxyManager()
        self._browser_manager = BrowserManager(self._proxy_manager)
        self._captcha_handler = CaptchaHandler()
        self._rate_limiter = RateLimiter(
            requests_per_minute=settings.scraper_rate_limit_rpm
        )
        self._context: BrowserContext | None = None
        self._max_retries = settings.scraper_max_retries
        self._timeout = settings.scraper_timeout

    async def initialize_browser(self) -> None:
        """Start the browser and create a context."""
        await self._browser_manager.start()
        self._context = await self._browser_manager.create_context()
        logger.info("Browser initialized", scraper=self.SCRAPER_NAME)

    async def create_context(self) -> BrowserContext:
        """Create a fresh isolated context."""
        return await self._browser_manager.create_context()

    async def close(self) -> None:
        """Close browser resources."""
        if self._context:
            await self._context.close()
        await self._browser_manager.close()
        logger.info("Scraper closed", scraper=self.SCRAPER_NAME)

    @abstractmethod
    async def scrape(self, keyword: str) -> list[dict]:
        """Subclasses implement their scraping logic here."""
        ...

    async def navigate_with_retry(
        self,
        page: Page,
        url: str,
        wait_until: str = "domcontentloaded",
    ) -> bool:
        """
        Navigate to a URL with retry on failure.
        Handles captchas automatically.
        """
        for attempt in range(1, self._max_retries + 1):
            try:
                await self._rate_limiter.acquire()
                await page.goto(
                    url,
                    timeout=self._timeout,
                    wait_until=wait_until,
                )
                await StealthManager.random_scroll(page)
                await StealthManager.random_delay(1.0, 2.5)

                # Handle captchas
                solved = await self._captcha_handler.detect_and_solve(page, url)
                if solved:
                    logger.info("Captcha solved, continuing", url=url[:60])

                return True

            except PWTimeout:
                logger.warning(
                    "Page timeout, retrying",
                    url=url[:60],
                    attempt=attempt,
                    max=self._max_retries,
                )
                await asyncio.sleep(random.uniform(3.0, 6.0))
            except Exception as e:
                logger.error(
                    "Navigation error",
                    url=url[:60],
                    attempt=attempt,
                    error=str(e),
                )
                if attempt == self._max_retries:
                    return False
                await asyncio.sleep(random.uniform(5.0, 10.0))

        return False

    async def retry_failed_request(self, coro_func, *args, **kwargs):  # type: ignore[no-untyped-def]
        """Generic retry wrapper for any coroutine."""
        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                last_error = e
                wait = min(2.0 * (2 ** (attempt - 1)), 30.0)
                logger.warning("Retrying", attempt=attempt, wait=wait, error=str(e))
                await asyncio.sleep(wait)
        raise last_error or RuntimeError("All retries exhausted")

    async def save_debug_artifacts(self, page: Page, label: str) -> None:
        """Save screenshot and HTML for debugging on error."""
        debug_dir = Path(settings.output_dir) / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        slug = label.replace(" ", "_")[:30]

        screenshot_path = debug_dir / f"{slug}_{timestamp}.png"
        html_path = debug_dir / f"{slug}_{timestamp}.html"

        try:
            await page.screenshot(path=str(screenshot_path), full_page=True)
            content = await page.content()
            html_path.write_text(content, encoding="utf-8")
            logger.info("Debug artifacts saved", screenshot=str(screenshot_path))
        except Exception as e:
            logger.error("Failed to save debug artifacts", error=str(e))
