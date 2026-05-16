"""
Web3 Scraper — Scrapes Web3/crypto job boards for QA/testing roles.

Targets: CryptoJobsList, Web3.career, Remote3
"""

from __future__ import annotations

import asyncio
import random

import structlog
from playwright.async_api import Page

from app.scraper.base_scraper import BaseScraper
from app.scraper.constants import WEB3_KEYWORDS, WEB3_PLATFORMS
from app.scraper.extractor import JobExtractor

logger = structlog.get_logger(__name__)


class Web3Scraper(BaseScraper):
    """
    Scrapes Web3 ecosystem job boards for smart contract QA,
    dApp testing, and crypto-native prompt engineer roles.
    """

    SCRAPER_NAME = "web3_jobs"

    def __init__(self) -> None:
        super().__init__()
        self._extractor = JobExtractor()

    async def scrape(self, keyword: str) -> list[dict]:
        """Scrape all Web3 platforms for a given keyword."""
        all_jobs: list[dict] = []
        await self.initialize_browser()

        try:
            for platform, url_template in WEB3_PLATFORMS.items():
                url = url_template.format(keyword=keyword.replace(" ", "-").lower())
                logger.info("Scraping Web3 platform", platform=platform, keyword=keyword)
                try:
                    jobs = await self._scrape_platform(platform, url)
                    all_jobs.extend(jobs)
                    await asyncio.sleep(random.uniform(2.0, 4.0))
                except Exception as e:
                    logger.error("Web3 platform failed", platform=platform, error=str(e))
        finally:
            await self.close()

        return all_jobs

    async def scrape_all_keywords(self) -> list[dict]:
        """Scrape all Web3 keywords across all platforms."""
        all_jobs: list[dict] = []
        await self.initialize_browser()

        try:
            for keyword in WEB3_KEYWORDS:
                for platform, url_template in WEB3_PLATFORMS.items():
                    url = url_template.format(keyword=keyword.replace(" ", "-").lower())
                    try:
                        jobs = await self._scrape_platform(platform, url)
                        all_jobs.extend(jobs)
                        await asyncio.sleep(random.uniform(3.0, 6.0))
                    except Exception as e:
                        logger.error("Web3 scrape error", keyword=keyword, error=str(e))
        finally:
            await self.close()

        # Deduplicate
        seen: set[str] = set()
        unique = [j for j in all_jobs if j.get("job_url") not in seen and not seen.add(j.get("job_url", ""))]
        logger.info("Web3 scrape complete", unique_jobs=len(unique))
        return unique

    async def _scrape_platform(self, platform: str, url: str) -> list[dict]:
        context = await self.create_context()
        page = await context.new_page()
        jobs: list[dict] = []

        try:
            success = await self.navigate_with_retry(page, url)
            if not success:
                return []

            html = await page.content()

            if platform == "cryptojobslist":
                jobs = await self._parse_cryptojobslist(page, html)
            elif platform == "web3career":
                jobs = await self._parse_web3career(page, html)
            elif platform == "remote3":
                jobs = await self._parse_remote3(page, html)

        except Exception as e:
            logger.error("Web3 parse error", platform=platform, error=str(e))
            await self.save_debug_artifacts(page, f"web3_{platform}_error")
        finally:
            await page.close()
            await context.close()

        return jobs

    async def _parse_cryptojobslist(self, page: Page, html: str) -> list[dict]:
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all("article.job")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("h2, h3, .job-title")
                    company_el = await card.query_selector(".company-name, .company")
                    location_el = await card.query_selector(".location, .remote")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else "Remote"
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://cryptojobslist.com{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="Web3 / Crypto role",
                            job_url=job_url or "https://cryptojobslist.com",
                            source_platform="cryptojobslist",
                        ))
                except Exception:
                    pass
        except Exception as e:
            logger.error("CryptoJobsList parse error", error=str(e))
        return jobs

    async def _parse_web3career(self, page: Page, html: str) -> list[dict]:
        jobs: list[dict] = []
        try:
            rows = await page.query_selector_all("tr.job_row, .job-card")
            for row in rows[:20]:
                try:
                    title_el = await row.query_selector("h2, .job-title, td:nth-child(2)")
                    company_el = await row.query_selector(".company, td:nth-child(1)")
                    link_el = await row.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://web3.career{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location="Remote",
                            description="Web3 career opportunity",
                            job_url=job_url or "https://web3.career",
                            source_platform="web3career",
                        ))
                except Exception:
                    pass
        except Exception as e:
            logger.error("Web3Career parse error", error=str(e))
        return jobs

    async def _parse_remote3(self, page: Page, html: str) -> list[dict]:
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job-card, article")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("h2, h3, .title")
                    company_el = await card.query_selector(".company, .org")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://remote3.co{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location="Remote",
                            description="Remote Web3 job",
                            job_url=job_url or "https://remote3.co",
                            source_platform="remote3",
                        ))
                except Exception:
                    pass
        except Exception as e:
            logger.error("Remote3 parse error", error=str(e))
        return jobs
