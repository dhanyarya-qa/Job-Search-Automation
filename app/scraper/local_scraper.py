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

        # Deduplicate by normalized URL (strips tracking params)
        seen_urls: set[str] = set()
        unique_jobs = []
        for job in all_jobs:
            url = job.get("job_url", "")
            # URL is already normalized by JobExtractor.build_job_dict(),
            # but normalize again for safety
            normalized = self._extractor.normalize_job_url(url) if url else ""
            if normalized and normalized not in seen_urls:
                seen_urls.add(normalized)
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
            elif platform == "indeed":
                jobs = await self._parse_indeed(page, html)
            elif platform == "dealls":
                jobs = await self._parse_dealls(page, html)
            elif platform == "karir":
                jobs = await self._parse_karir(page, html)
            elif platform == "urbanhire":
                jobs = await self._parse_urbanhire(page, html)

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

    async def _parse_indeed(self, page: Page, html: str) -> list[dict]:
        """Parse Indeed job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job_seen_beacon")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector("h2.jobTitle")
                    company_el = await card.query_selector("[data-testid='company-name']")
                    location_el = await card.query_selector("[data-testid='text-location']")
                    salary_el = await card.query_selector(".salary-snippet")
                    link_el = await card.query_selector("a.jcs-JobTitle")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    salary = await salary_el.inner_text() if salary_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://id.indeed.com{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            salary=salary,
                            job_url=job_url or "https://id.indeed.com",
                            source_platform="indeed",
                            html_content=html,
                        ))
                except Exception as e:
                    logger.debug("Indeed card error", error=str(e))
        except Exception as e:
            logger.error("Indeed parse failed", error=str(e))
        return jobs

    async def _parse_dealls(self, page: Page, html: str) -> list[dict]:
        """Parse Dealls.com job listings.
        
        Dealls uses cards wrapped in <a href="/loker/..."> with:
        - h2 for job title
        - sibling div after h2 for company name  
        - span elements for job type, location, experience, salary
        """
        jobs: list[dict] = []
        try:
            # Click "Lebih Banyak" (Show More) to load all jobs if available
            try:
                show_more = await page.query_selector("text=Lebih Banyak")
                if show_more:
                    await show_more.click()
                    await asyncio.sleep(2)  # Wait for dynamic load
            except Exception:
                pass  # No show more button or already expanded

            # Job cards are <a> links with href starting with /loker/
            cards = await page.query_selector_all("a[href^='/loker/']")
            for card in cards[:20]:
                try:
                    # Title is in h2
                    title_el = await card.query_selector("h2")
                    title = await title_el.inner_text() if title_el else ""

                    # Company name is the div right after h2
                    company = ""
                    if title_el:
                        company_el = await title_el.evaluate_handle(
                            "(el) => el.nextElementSibling"
                        )
                        if company_el:
                            company = await company_el.inner_text() or ""

                    # Get href for job URL
                    href = await card.get_attribute("href") or ""
                    job_url = f"https://dealls.com{href}" if href.startswith("/") else href

                    # Extract span elements for metadata
                    spans = await card.query_selector_all("span")
                    location = ""
                    salary = ""
                    job_type = ""
                    experience_level = ""
                    is_remote = False

                    for span in spans:
                        text = (await span.inner_text()).strip()
                        if not text:
                            continue

                        # Location contains bullet separator (e.g. "Hybrid • Jakarta")
                        if "\u2022" in text or "•" in text:
                            location = text
                            # Check remote/WFH
                            lower = text.lower()
                            if any(w in lower for w in ["remote", "wfh", "work from home"]):
                                is_remote = True

                        # Salary contains "Rp" or "Negotiable"
                        elif "Rp" in text or "negotiable" in text.lower():
                            salary = text

                        # Experience contains "Min." or "Years"
                        elif "min." in text.lower() or "years" in text.lower() or "tahun" in text.lower():
                            experience_level = text

                    # Job type from button element
                    type_el = await card.query_selector("button")
                    if type_el:
                        type_text = (await type_el.inner_text()).strip()
                        # Map Indonesian to English
                        type_map = {
                            "penuh waktu": "Full-time",
                            "paruh waktu": "Part-time",
                            "kontrak": "Contract",
                            "magang": "Internship",
                            "freelance": "Freelance",
                        }
                        job_type = type_map.get(type_text.lower(), type_text)

                    if title and job_url:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            salary=salary if salary.lower() != "negotiable" else "",
                            job_url=job_url,
                            source_platform="dealls",
                            job_type=job_type,
                            experience_level=experience_level,
                            is_remote=is_remote,
                        ))
                except Exception as e:
                    logger.debug("Dealls card error", error=str(e))
        except Exception as e:
            logger.error("Dealls parse failed", error=str(e))
        return jobs

    async def _parse_karir(self, page: Page, html: str) -> list[dict]:
        """Parse Karir.com job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job-item, .job-list-item")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector(".job-title, h3")
                    company_el = await card.query_selector(".company-name, .company")
                    location_el = await card.query_selector(".location, .job-location")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://www.karir.com{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            job_url=job_url or "https://www.karir.com",
                            source_platform="karir",
                        ))
                except Exception as e:
                    logger.debug("Karir card error", error=str(e))
        except Exception as e:
            logger.error("Karir parse failed", error=str(e))
        return jobs

    async def _parse_urbanhire(self, page: Page, html: str) -> list[dict]:
        """Parse Urbanhire job listings."""
        jobs: list[dict] = []
        try:
            cards = await page.query_selector_all(".job-card, .job-item")
            for card in cards[:20]:
                try:
                    title_el = await card.query_selector(".job-title, h3")
                    company_el = await card.query_selector(".company-name, .company")
                    location_el = await card.query_selector(".location, .job-location")
                    salary_el = await card.query_selector(".salary")
                    link_el = await card.query_selector("a")

                    title = await title_el.inner_text() if title_el else ""
                    company = await company_el.inner_text() if company_el else ""
                    location = await location_el.inner_text() if location_el else ""
                    salary = await salary_el.inner_text() if salary_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    job_url = f"https://www.urbanhire.com{href}" if href and href.startswith("/") else href

                    if title and company:
                        jobs.append(self._extractor.build_job_dict(
                            job_title=title,
                            company_name=company,
                            location=location,
                            description="",
                            salary=salary,
                            job_url=job_url or "https://www.urbanhire.com",
                            source_platform="urbanhire",
                        ))
                except Exception as e:
                    logger.debug("Urbanhire card error", error=str(e))
        except Exception as e:
            logger.error("Urbanhire parse failed", error=str(e))
        return jobs
