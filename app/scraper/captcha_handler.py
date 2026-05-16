"""
Captcha Handler — Anti-captcha integration with reCAPTCHA/hCaptcha detection.
"""

from __future__ import annotations

import asyncio

import structlog
from playwright.async_api import Page

from app.config import settings

logger = structlog.get_logger(__name__)


class CaptchaHandler:
    """
    Detects and solves reCAPTCHA v2, hCaptcha, and iframe captchas
    using the AntiCaptcha API.
    """

    RECAPTCHA_SELECTORS = [
        "iframe[src*='recaptcha']",
        ".g-recaptcha",
        "#g-recaptcha",
    ]
    HCAPTCHA_SELECTORS = [
        "iframe[src*='hcaptcha']",
        ".h-captcha",
        "#h-captcha",
    ]

    def __init__(self) -> None:
        self._api_key = settings.anticaptcha_api_key

    async def detect_and_solve(self, page: Page, url: str) -> bool:
        """
        Detect captcha type, solve, inject token, return True if handled.
        """
        captcha_type = await self._detect_captcha(page)
        if not captcha_type:
            return False

        logger.info("Captcha detected", type=captcha_type, url=url)

        if captcha_type == "recaptcha":
            return await self._solve_recaptcha(page, url)
        elif captcha_type == "hcaptcha":
            return await self._solve_hcaptcha(page, url)
        return False

    async def _detect_captcha(self, page: Page) -> str | None:
        """Detect which captcha type is present on the page."""
        for selector in self.RECAPTCHA_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    return "recaptcha"
            except Exception:
                pass

        for selector in self.HCAPTCHA_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    return "hcaptcha"
            except Exception:
                pass

        return None

    async def _extract_site_key(self, page: Page, captcha_type: str) -> str | None:
        """Extract site key from the captcha element."""
        if captcha_type == "recaptcha":
            return await page.evaluate(
                "() => { const el = document.querySelector('.g-recaptcha'); "
                "return el ? el.getAttribute('data-sitekey') : null; }"
            )
        elif captcha_type == "hcaptcha":
            return await page.evaluate(
                "() => { const el = document.querySelector('.h-captcha'); "
                "return el ? el.getAttribute('data-sitekey') : null; }"
            )
        return None

    async def _solve_recaptcha(self, page: Page, url: str) -> bool:
        """Solve reCAPTCHA v2 via AntiCaptcha API."""
        if not self._api_key:
            logger.warning("AntiCaptcha API key not configured")
            return False

        try:
            from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless  # noqa: PLC0415

            site_key = await self._extract_site_key(page, "recaptcha")
            if not site_key:
                logger.warning("Could not extract reCAPTCHA site key")
                return False

            solver = recaptchaV2Proxyless()
            solver.set_verbose(0)
            solver.set_key(self._api_key)
            solver.set_website_url(url)
            solver.set_website_key(site_key)

            token = solver.solve_and_return_solution()
            if not token:
                logger.error("AntiCaptcha returned no token", error=solver.error_code)
                return False

            # Inject token
            await page.evaluate(
                f"document.getElementById('g-recaptcha-response').innerHTML = '{token}';"
            )
            logger.info("reCAPTCHA solved and injected")
            return True

        except Exception as e:
            logger.error("reCAPTCHA solving failed", error=str(e))
            return False

    async def _solve_hcaptcha(self, page: Page, url: str) -> bool:
        """Solve hCaptcha via AntiCaptcha API."""
        if not self._api_key:
            return False

        try:
            from anticaptchaofficial.hcaptchaproxyless import hCaptchaProxyless  # noqa: PLC0415

            site_key = await self._extract_site_key(page, "hcaptcha")
            if not site_key:
                return False

            solver = hCaptchaProxyless()
            solver.set_verbose(0)
            solver.set_key(self._api_key)
            solver.set_website_url(url)
            solver.set_website_key(site_key)

            token = solver.solve_and_return_solution()
            if not token:
                logger.error("hCaptcha solver returned no token")
                return False

            await page.evaluate(
                f"document.querySelector('[name=h-captcha-response]').value = '{token}';"
            )
            logger.info("hCaptcha solved and injected")
            return True

        except Exception as e:
            logger.error("hCaptcha solving failed", error=str(e))
            return False
