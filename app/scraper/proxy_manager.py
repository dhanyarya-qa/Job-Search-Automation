"""
Proxy Manager — Rotating proxy pool for anti-detection.
"""

from __future__ import annotations

import asyncio
import itertools
import random

import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class ProxyManager:
    """
    Manages a rotating proxy pool.
    Falls back to direct connection if no proxies are configured.
    """

    def __init__(self) -> None:
        self._proxies: list[str] = settings.proxy_list_parsed
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None
        self._failed: set[str] = set()
        self._lock = asyncio.Lock()

    def has_proxies(self) -> bool:
        return bool(self._proxies) and settings.use_proxy

    async def get_proxy(self) -> dict | None:
        """
        Return next proxy dict for Playwright context, or None for direct.
        """
        if not self.has_proxies():
            return None
        async with self._lock:
            available = [p for p in self._proxies if p not in self._failed]
            if not available:
                logger.warning("All proxies failed, clearing failed list")
                self._failed.clear()
                available = self._proxies[:]
            proxy_url = random.choice(available)
            logger.debug("Using proxy", proxy=proxy_url[:30])
            return {"server": proxy_url}

    async def mark_failed(self, proxy_url: str) -> None:
        """Mark a proxy as failed so it gets skipped."""
        async with self._lock:
            self._failed.add(proxy_url)
            logger.warning("Proxy marked as failed", proxy=proxy_url[:30])

    def proxy_count(self) -> int:
        return len(self._proxies)
