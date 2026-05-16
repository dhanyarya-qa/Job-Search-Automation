"""
Stealth Manager — Playwright-stealth integration and human behavior simulation.
"""

from __future__ import annotations

import asyncio
import random

import structlog
from playwright.async_api import BrowserContext, Page

from app.scraper.constants import (
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
    HUMAN_MOUSE_MOVE_STEPS,
    HUMAN_TYPING_DELAY_MAX,
    HUMAN_TYPING_DELAY_MIN,
    VIEWPORT_VARIANTS,
)

logger = structlog.get_logger(__name__)


class StealthManager:
    """
    Applies stealth patches and simulates human-like browser behavior
    to avoid bot detection systems.
    """

    @staticmethod
    async def apply_stealth(context: BrowserContext) -> None:
        """Apply stealth JS patches to a browser context."""
        try:
            from playwright_stealth import stealth_async  # noqa: PLC0415
            # Apply stealth to each new page
            context.on("page", lambda page: asyncio.ensure_future(stealth_async(page)))
        except ImportError:
            logger.warning("playwright-stealth not installed, skipping stealth patches")

    @staticmethod
    def get_random_viewport() -> dict[str, int]:
        """Return a random viewport size from realistic variants."""
        return random.choice(VIEWPORT_VARIANTS)

    @staticmethod
    def get_random_user_agent() -> str:
        """Return a randomized user agent string."""
        try:
            from fake_useragent import UserAgent  # noqa: PLC0415
            ua = UserAgent(browsers=["chrome", "firefox", "edge"])
            return ua.random
        except Exception:
            # Fallback realistic UA
            return (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )

    @staticmethod
    async def human_type(page: Page, selector: str, text: str) -> None:
        """Type text character-by-character with human-like delays."""
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char)
            delay = random.uniform(HUMAN_TYPING_DELAY_MIN, HUMAN_TYPING_DELAY_MAX)
            await asyncio.sleep(delay / 1000)

    @staticmethod
    async def human_mouse_move(page: Page, x: int, y: int) -> None:
        """Move mouse to coordinates with human-like curved path."""
        current_x = random.randint(0, 800)
        current_y = random.randint(0, 600)
        steps = HUMAN_MOUSE_MOVE_STEPS
        for step in range(1, steps + 1):
            next_x = int(current_x + (x - current_x) * step / steps)
            next_y = int(current_y + (y - current_y) * step / steps)
            await page.mouse.move(next_x, next_y)
            await asyncio.sleep(random.uniform(0.01, 0.03))

    @staticmethod
    async def random_scroll(page: Page) -> None:
        """Perform random scrolling to simulate reading behavior."""
        scroll_count = random.randint(2, 5)
        for _ in range(scroll_count):
            scroll_y = random.randint(300, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_y})")
            await asyncio.sleep(random.uniform(0.5, 1.5))

    @staticmethod
    async def random_delay(min_s: float = 1.0, max_s: float = 3.0) -> None:
        """Wait a random amount of time."""
        await asyncio.sleep(random.uniform(min_s, max_s))
