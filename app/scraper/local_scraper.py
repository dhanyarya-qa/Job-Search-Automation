"""
Local Job Scraper — Scrapes local Indonesian job portals.

Targets: LinkedIn, JobStreet, Glints, Kalibrr
"""

from __future__ import annotations

import asyncio
import random

import structlog
from playwright.async_api import Page

from app.scraper.base_scraper import BaseScraper
from app.scraper.constants import JOB_KEYWORDS, LOCAL_PLATFORMS
from app.scraper.extractor import JobExtractor

logger = structlog.get_logger(__name__)


class LocalJobScraper(BaseScraper):
    """
    Scrapes local Indonesian job portals with full stealth and anti-bot measures.
    Supports LinkedIn, JobStreet, Glints, and Kalibrr.
    """

    SCRAPER_NAME = "local_jobs"

    def __init__(self) -> None:
        super().__init__()
        self._extractor = JobExtractor()

    async def scrape(self, keyword: str) -> list[dict]:
        """
        Scrape all configured local platforms for a given keyword.
        Returns combined list of job dicts.
        """
        all_jobs: list[dict] = []
        await self.initialize_browser()

        try:
            for platform, url_template in LOCAL_PLATFORMS.items():
                url = url_template.format(keyword=keyword.replace(" ", "+"))
                logger.info("Scraping platform", platform=platform, keyword=keyword)
                try:
                    jobs = await self._scrape_platform(platform, url)
                    all_jobs.extend(jobs)
                    logger.info("Platform scraped", platform=platform, count=len(jobs))
                except Exception as e:
                    logger.error("Platform scrape failed", platform=platform, error=str(e))

        finally:
            await self.close()

        return all_jobs

    async def scrape_all_keywords(self) -> list[dict]:
        """Scrape all configured keywords across all platforms."""
        all_jobs: list[dict] = []
        await self.initialize_browser()

        try:
            for keyword in JOB_KEYWORDS:
                for platform, url_template in LOCAL_PLATFORMS.items():
                    url = url_template.format(keyword=keyword.replace(" ", "+"))
                    try:
                        jobs = await self._scrape_platform(platform, url)
                        all_jobs.extend(jobs)
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                    except Exception as e:
                        logger.error(
                            "Failed keyword/platform",
                            keyword=keyword,
                            platform=platform,
                            error=str(e),
                        )
        finally:
            await self.close()

        # Deduplicate by URL
        seen_urls: set[str] = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get("job_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)

        logger.info("Scraping complete", total=len(unique_jobs), duplicates_removed=len(all_jobs) - len(unique_jobs))
        return unique_jobs

    async def _scrape_platform(self, platform: str, url: str) -> list[dict]:
        """Route to the correct platform-specific scraper."""
        context = await self.create_context()
        page = await context.new_page()
        jobs: list[dict] = []

        try:
            success = await self.navigate_with_retry(page, url)
            if not success:
                logger.warning("Navigation failed", platform=platform, url=url[:60])
                return []

            html = await page.content()

            if platform == "linkedin":
                jobs = await self._parse_linkedin(page, html)
            elif platform == "jobstreet":
                jobs = await self._parse_jobstreet(page, html)
            elif platform == "glints":
                jobs = await self._parse_glints(page, html)
            elif platform == "kalibrr":
                jobs = await self._parse_kalibrr(page, html)

        except Exception as e:
            logger.error("Platform parse error", platform=platform, error=str(e))
            await self.save_debug_artifacts(page, f"{platform}_error")
        finally:
            await page.close()
            await context.close()

        return jobs

    async def _parse_linkedin(self, page: Page, html: str) -> list[dict]:
        """Parse LinkedIn job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job-search-card")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector(".base-search-card__title")
                    company_el = await card.query_selector(".base-search-card__subtitle")
                    location_el = await card.query_selector(".job-search-card__location")
                    link_el = await card.query_selector("a.base-card__full-link")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    job_url = await link_el.get_attribute("href") if link_el else ""

                    if title and company and job_url:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            job_url=job_url,
                            source_platform="linkedin",
                            html_content=html,
                        ))
                except Exception as e:
                    logger.debug("Card parse error", error=str(e))
        except Exception as e:
            logger.error("LinkedIn parse failed", error=str(e))
        return jobs

    async def _parse_jobstreet(self, page: Page, html: str) -> list[dict]:
        """Parse JobStreet job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all("[data-automation='jobCard']")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("[data-automation='jobTitle']")
                    company_el = await card.query_selector("[data-automation='jobCompany']")
                    location_el = await card.query_selector("[data-automation='jobLocation']")
                    salary_el = await card.query_selector("[data-automation='jobSalary']")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    salary = await salary_el.inner_text() if salary_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://www.jobstreet.co.id{href}" if href and href.startswith("/") else href

                    if title and company and job_url:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            salary=salary,
                            job_url=job_url,
                            source_platform="jobstreet",
                            html_content=html,
                        ))
                except Exception as e:
                    logger.debug("JobStreet card error", error=str(e))
        except Exception as e:
            logger.error("JobStreet parse failed", error=str(e))
        return jobs

    async def _parse_glints(self, page: Page, html: str) -> list[dict]:
        """Parse Glints job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".JobCardsc__JobcardContainer")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("h2")
                    company_el = await card.query_selector("span.company-name")
                    location_el = await card.query_selector("[class*='location']")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://glints.com{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            job_url=job_url or "https://glints.com",
                            source_platform="glints",
                        ))
                except Exception as e:
                    logger.debug("Glints card error", error=str(e))
        except Exception as e:
            logger.error("Glints parse failed", error=str(e))
        return jobs

    async def _parse_kalibrr(self, page: Page, html: str) -> list[dict]:
        """Parse Kalibrr job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job-card")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector(".job-title")
                    company_el = await card.query_selector(".company-name")
                    location_el = await card.query_selector(".location")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://www.kalibrr.id{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            job_url=job_url or "https://www.kalibrr.id",
                            source_platform="kalibrr",
                        ))
                except Exception as e:
                    logger.debug("Kalibrr card error", error=str(e))
        except Exception as e:
            logger.error("Kalibrr parse failed", error=str(e))
        return jobs
