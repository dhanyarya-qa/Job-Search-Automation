"""
Rate Limiter — Token bucket rate limiter for scraping requests.
"""

from __future__ import annotations

import asyncio
import time

import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """
    Async token bucket rate limiter.
    Enforces max requests-per-minute with burst tolerance.
    """

    def __init__(self, requests_per_minute: int = 30, burst_limit: int = 10) -> None:
        self.rpm = requests_per_minute
        self.burst_limit = burst_limit
        self._tokens: float = float(burst_limit)
        self._last_refill: float = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Block until a request token is available."""
        async with self._lock:
            await self._refill()
            while self._tokens < 1.0:
                wait = (1.0 - self._tokens) / (self.rpm / 60.0)
                logger.debug("Rate limit: waiting", wait_seconds=round(wait, 2))
                await asyncio.sleep(wait)
                await self._refill()
            self._tokens -= 1.0

    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        added = elapsed * (self.rpm / 60.0)
        self._tokens = min(self._tokens + added, float(self.burst_limit))
        self._last_refill = now
