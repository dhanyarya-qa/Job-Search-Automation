"""
Tech Stack Profiler — Detects company tech stack via HTML/header fingerprinting.
"""

from __future__ import annotations

import structlog
import aiohttp
from bs4 import BeautifulSoup

from app.scraper.constants import TECH_FINGERPRINTS

logger = structlog.get_logger(__name__)


class TechStackProfiler:
    """
    Profiles a company's tech stack by inspecting:
    - HTML meta tags
    - JavaScript bundle names
    - HTTP response headers
    - Inline script content

    Output is sent to the AI Engine for context-aware scoring.
    """

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
                    )
                },
            )
        return self._session

    async def profile(self, url: str) -> dict[str, list[str] | str]:
        """
        Fetch and analyze a company website to detect its tech stack.
        Returns dict with detected technologies and confidence.
        """
        if not url or not url.startswith("http"):
            return {"detected": [], "confidence": "none", "url": url}

        try:
            session = await self._get_session()
            async with session.get(url, allow_redirects=True, ssl=False) as resp:
                html_content = await resp.text(errors="replace")
                response_headers = dict(resp.headers)
                final_url = str(resp.url)

            detected = self._analyze(html_content, response_headers)
            logger.info("Tech stack profiled", url=final_url, detected=detected)

            return {
                "url": final_url,
                "detected": detected,
                "confidence": self._calculate_confidence(detected),
                "raw_signals": len(detected),
            }

        except aiohttp.ClientError as e:
            logger.warning("Failed to profile URL", url=url, error=str(e))
            return {"detected": [], "confidence": "error", "url": url, "error": str(e)}
        except Exception as e:
            logger.error("Unexpected profiler error", url=url, error=str(e))
            return {"detected": [], "confidence": "error", "url": url}

    def _analyze(self, html: str, headers: dict[str, str]) -> list[str]:
        """Run all detection methods and return unique tech list."""
        detected: set[str] = set()
        html_lower = html.lower()
        combined = html_lower + " ".join(f"{k}:{v}".lower() for k, v in headers.items())

        for tech, signals in TECH_FINGERPRINTS.items():
            for signal in signals:
                if signal.lower() in combined:
                    detected.add(tech)
                    break

        # Additional header-based detection
        server = headers.get("Server", "").lower()
        powered_by = headers.get("X-Powered-By", "").lower()

        if "nginx" in server:
            detected.add("Nginx")
        if "apache" in server:
            detected.add("Apache")
        if "express" in powered_by:
            detected.add("Node.js")
            detected.add("Express")
        if "php" in powered_by:
            detected.add("PHP")

        # Meta tag analysis
        soup = BeautifulSoup(html, "html.parser")
        generator = soup.find("meta", {"name": "generator"})
        if generator and generator.get("content"):
            content = str(generator["content"]).lower()
            if "wordpress" in content:
                detected.add("WordPress")
            elif "drupal" in content:
                detected.add("Drupal")
            elif "next" in content:
                detected.add("Next.js")

        return sorted(detected)

    @staticmethod
    def _calculate_confidence(detected: list[str]) -> str:
        count = len(detected)
        if count >= 5:
            return "high"
        elif count >= 2:
            return "medium"
        elif count >= 1:
            return "low"
        return "none"

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
