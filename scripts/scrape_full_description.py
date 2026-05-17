"""
Scrape Full Job Description - Get detailed job information
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from playwright.async_api import async_playwright
from sqlalchemy import select
from app.database.session import get_async_session
from app.database.models.job import Job

logger = structlog.get_logger(__name__)


async def scrape_linkedin_full_description(url: str) -> dict:
    """Scrape full LinkedIn job description"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Get full description
            desc_el = await page.query_selector(".show-more-less-html__markup")
            description = await desc_el.inner_text() if desc_el else ""
            
            # Get requirements
            requirements = []
            req_section = await page.query_selector(".description__text")
            if req_section:
                req_text = await req_section.inner_text()
                requirements = [line.strip() for line in req_text.split("\n") if line.strip()]
            
            await browser.close()
            
            return {
                "description": description,
                "requirements": requirements,
            }
    except Exception as e:
        logger.error("LinkedIn scrape failed", error=str(e))
        return {"description": "", "requirements": []}


async def scrape_jobstreet_full_description(url: str) -> dict:
    """Scrape full JobStreet job description"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Get full description
            desc_el = await page.query_selector("[data-automation='jobDescription']")
            description = await desc_el.inner_text() if desc_el else ""
            
            # Get job details
            details = {}
            detail_items = await page.query_selector_all("[data-automation='job-detail-item']")
            for item in detail_items:
                label_el = await item.query_selector("[data-automation='job-detail-label']")
                value_el = await item.query_selector("[data-automation='job-detail-value']")
                
                if label_el and value_el:
                    label = await label_el.inner_text()
                    value = await value_el.inner_text()
                    details[label] = value
            
            await browser.close()
            
            return {
                "description": description,
                "details": details,
            }
    except Exception as e:
        logger.error("JobStreet scrape failed", error=str(e))
        return {"description": "", "details": {}}


async def scrape_full_description(job_url: str, platform: str) -> dict:
    """Scrape full job description based on platform"""
    print(f"🔍 Scraping: {job_url[:60]}...")
    
    if "linkedin" in platform:
        return await scrape_linkedin_full_description(job_url)
    elif "jobstreet" in platform:
        return await scrape_jobstreet_full_description(job_url)
    else:
        # Generic scraper
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(job_url, timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Try to get main content
                content = await page.content()
                
                await browser.close()
                
                return {"description": content[:5000], "raw_html": True}
        except Exception as e:
            logger.error("Generic scrape failed", error=str(e))
            return {"description": "", "raw_html": False}


async def update_job_descriptions():
    """Update job descriptions for jobs without full details"""
    print("=" * 60)
    print("📝 UPDATING JOB DESCRIPTIONS")
    print("=" * 60)
    print()
    
    async for session in get_async_session():
        # Get jobs without full description (empty or short)
        result = await session.execute(
            select(Job)
            .where(
                (Job.description == "") | 
                (Job.description == None) |
                (Job.description.like("%...%"))  # Truncated descriptions
            )
            .limit(10)  # Process 10 at a time
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("✅ All jobs have full descriptions")
            return
        
        print(f"📦 Found {len(jobs)} jobs to update\n")
        
        for i, job in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {job.job_title} - {job.company_name}")
            
            try:
                # Scrape full description
                full_data = await scrape_full_description(job.job_url, job.source_platform)
                
                # Update job
                if full_data.get("description"):
                    job.description = full_data["description"]
                    
                    if "requirements" in full_data:
                        import json
                        job.requirements = json.dumps(full_data["requirements"])
                    
                    await session.commit()
                    print(f"  ✅ Updated ({len(full_data['description'])} chars)")
                else:
                    print(f"  ⚠️  No description found")
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error("Update failed", job_id=job.id, error=str(e))
                print(f"  ❌ Error: {e}")
        
        print()
        print("=" * 60)
        print(f"✅ Updated {len(jobs)} job descriptions")
        print("=" * 60)


async def main():
    await update_job_descriptions()


if __name__ == "__main__":
    asyncio.run(main())
