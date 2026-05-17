"""
LinkedIn Post Scraper — Scrapes LinkedIn posts/feed for job opportunities using Google Search.

This scraper searches for LinkedIn posts (not job listings) using Google with site:linkedin.com/posts
to find hiring posts from companies and individuals.

Keywords: QA Automation, QA Manual, Software Tester, Prompt Engineer, AI Engineer, etc.
"""

from __future__ import annotations

import asyncio
import random
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

import structlog
from playwright.async_api import Page

from app.scraper.base_scraper import BaseScraper
from app.scraper.constants import JOB_KEYWORDS
from app.scraper.extractor import JobExtractor

logger = structlog.get_logger(__name__)


class LinkedInPostScraper(BaseScraper):
    """
    Scrapes LinkedIn posts for job opportunities using Google Search.
    More reliable than direct LinkedIn scraping (no login required).
    """

    SCRAPER_NAME = "linkedin_posts"

    def __init__(self) -> None:
        super().__init__()
        self._extractor = JobExtractor()

    async def scrape(self, keyword: str) -> list[dict]:
        """
        Main scrape method (required by BaseScraper).
        Scrapes LinkedIn posts for a given keyword using Google Search.
        """
        return await self.scrape_posts(keyword, max_posts=10)

    async def scrape_posts(self, keyword: str, max_posts: int = 10) -> list[dict]:
        """
        Scrape LinkedIn posts for job opportunities using Google Search.
        
        Args:
            keyword: Search keyword (e.g., "QA Automation")
            max_posts: Maximum number of posts to scrape
            
        Returns:
            List of post dictionaries with complete information
        """
        all_posts: list[dict] = []
        await self.initialize_browser()

        try:
            # Use Google to search for LinkedIn posts about hiring
            # site:linkedin.com/posts "hiring" OR "we're hiring" "QA Automation"
            search_query = f'site:linkedin.com/posts ("hiring" OR "we are hiring" OR "join our team") "{keyword}"'
            google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&num=20"
            
            logger.info("Searching LinkedIn posts via Google", keyword=keyword)
            
            context = await self.create_context()
            page = await context.new_page()

            try:
                # Navigate to Google search
                success = await self.navigate_with_retry(page, google_url)
                if not success:
                    logger.warning("Navigation failed", url=google_url[:60])
                    return []

                # Wait for results
                await asyncio.sleep(2)
                
                # Extract LinkedIn post URLs from Google results
                post_urls = await self._extract_post_urls_from_google(page)
                logger.info("Found LinkedIn post URLs", count=len(post_urls))
                
                # Visit each post and extract job information
                for i, post_url in enumerate(post_urls[:max_posts]):
                    try:
                        logger.info(f"Processing post {i+1}/{min(len(post_urls), max_posts)}", url=post_url[:60])
                        
                        # Navigate to the LinkedIn post
                        await page.goto(post_url, wait_until="domcontentloaded", timeout=15000)
                        await asyncio.sleep(2)
                        
                        # Extract post content
                        post_data = await self._extract_post_content(page, keyword, post_url)
                        if post_data:
                            all_posts.append(post_data)
                            logger.info("Post extracted", title=post_data.get("job_title", "")[:30])
                        
                        await asyncio.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        logger.debug("Post extraction error", url=post_url[:60], error=str(e))
                
            except Exception as e:
                logger.error("Google search error", error=str(e))
            finally:
                await page.close()
                await context.close()

        finally:
            await self.close()

        return all_posts

    async def _extract_post_urls_from_google(self, page: Page) -> list[str]:
        """Extract LinkedIn post URLs from Google search results."""
        urls: list[str] = []
        
        try:
            # Google search result links
            links = await page.query_selector_all("a[href*='linkedin.com/posts/']")
            
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    if href and "linkedin.com/posts/" in href:
                        # Clean up Google redirect URL
                        if href.startswith("/url?q="):
                            href = href.split("/url?q=")[1].split("&")[0]
                        
                        # Only add unique URLs
                        if href not in urls and href.startswith("http"):
                            urls.append(href)
                except:
                    pass
                    
        except Exception as e:
            logger.error("Failed to extract URLs from Google", error=str(e))
            
        return urls

    async def _extract_post_content(self, page: Page, keyword: str, post_url: str) -> dict | None:
        """Extract job information from a LinkedIn post."""
        try:
            # Try to get post content (LinkedIn may show limited content without login)
            content = ""
            
            # Try multiple selectors for post content
            selectors = [
                ".feed-shared-update-v2__description",
                ".feed-shared-text",
                "[data-test-id='main-feed-activity-card__commentary']",
                ".break-words",
            ]
            
            for selector in selectors:
                try:
                    content_el = await page.query_selector(selector)
                    if content_el:
                        content = await content_el.inner_text()
                        if content and len(content) > 50:
                            break
                except:
                    pass
            
            # If no content found, try getting page text
            if not content or len(content) < 50:
                try:
                    body = await page.query_selector("body")
                    if body:
                        content = await body.inner_text()
                except:
                    pass
            
            # Check if content is about hiring
            if not self._is_job_post(content):
                return None
            
            # Extract author/company name
            author = "LinkedIn User"
            try:
                author_el = await page.query_selector(".update-components-actor__name, .feed-shared-actor__name")
                if author_el:
                    author = await author_el.inner_text()
            except:
                pass
            
            # Extract job title from content
            job_title = self._extract_job_title(content) or f"{keyword} Position"
            
            # Extract location
            location = self._extract_location(content) or "Remote/Indonesia"
            
            # Extract salary
            salary = self._extractor.extract_salary(content)
            
            # Extract email
            apply_email = self._extractor.extract_email(content)
            
            # Build job dict
            return self._extractor.build_job_dict(
                job_title=job_title,
                company_name=author,
                location=location,
                description=content[:1000],  # Limit description
                job_url=post_url,
                source_platform="linkedin_post",
                salary=salary,
                apply_email=apply_email,
                html_content=content,
            )
            
        except Exception as e:
            logger.debug("Post content extraction error", error=str(e))
            return None

    def _is_job_post(self, content: str) -> bool:
        """Check if post content is about a job opportunity."""
        if not content or len(content) < 30:
            return False
            
        content_lower = content.lower()
        
        # Job-related keywords
        job_indicators = [
            "hiring", "we're hiring", "we are hiring", "join our team", "join us",
            "looking for", "seeking", "open position", "vacancy", "lowongan",
            "apply now", "send cv", "send resume", "interested candidates",
            "job opening", "career opportunity", "we need", "urgently needed",
            "recruitment", "rekrutmen", "dicari", "dibutuhkan", "apply here",
        ]
        
        return any(indicator in content_lower for indicator in job_indicators)

    def _extract_job_title(self, content: str) -> str:
        """Extract job title from post content."""
        # Common patterns for job titles in posts
        patterns = [
            r"(?:hiring|looking for|seeking|need)\s+(?:a\s+)?([A-Z][A-Za-z\s]+(?:Engineer|Developer|Tester|QA|Analyst|Manager|Designer|Architect))",
            r"(?:position|role|vacancy):\s*([A-Z][A-Za-z\s]+)",
            r"([A-Z][A-Za-z\s]+(?:Engineer|Developer|Tester|QA|Analyst|Manager|Designer|Architect))\s+(?:needed|required|wanted|position)",
            r"#(\w+(?:Engineer|Developer|Tester|QA|Jobs))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up hashtags
                title = title.replace("#", "").replace("Jobs", " ")
                return title
        
        return ""

    def _extract_location(self, content: str) -> str:
        """Extract location from post content."""
        # Common location patterns
        patterns = [
            r"(?:location|lokasi):\s*([A-Za-z\s,]+)",
            r"(?:based in|located in)\s+([A-Za-z\s,]+)",
            r"(Jakarta|Bandung|Surabaya|Bali|Indonesia|Remote|WFH|Work from home)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return ""


async def main():
    """Test the LinkedIn post scraper."""
    print("=" * 60)
    print("🔍 LinkedIn Post Scraper Test (via Google)")
    print("=" * 60)
    
    scraper = LinkedInPostScraper()
    
    # Test with one keyword
    keyword = "QA Automation"
    print(f"\nSearching for: {keyword}")
    
    posts = await scraper.scrape_posts(keyword, max_posts=5)
    
    print(f"\n✅ Found {len(posts)} job posts")
    
    for i, post in enumerate(posts, 1):
        print(f"\n[{i}] {post.get('job_title', 'N/A')}")
        print(f"    Company: {post.get('company_name', 'N/A')}")
        print(f"    Location: {post.get('location', 'N/A')}")
        print(f"    URL: {post.get('job_url', 'N/A')[:60]}...")
        print(f"    Content: {post.get('description', 'N/A')[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
