"""
Optimized Job Finder - Fast scraping with immediate Telegram notifications
Scrapes one keyword at a time to avoid long waits
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.scraper.local_scraper import LocalJobScraper
from app.scraper.filters import JobFilter, DEFAULT_FILTER
from app.notifications.telegram_notifier import TelegramNotifier
from app.database.session import get_async_session
from app.database.models.job import Job
from sqlalchemy import select
from app.scraper.constants import JOB_KEYWORDS
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)


async def send_job_to_telegram(notifier: TelegramNotifier, job: dict) -> bool:
    """Send job notification to Telegram with apply info and buttons"""
    
    title = job.get("job_title", "Unknown Position")
    company = job.get("company_name", "Unknown Company")
    location = job.get("location", "Location not specified")
    platform = job.get("source_platform", "")
    job_url = job.get("job_url", "")
    apply_email = job.get("apply_email", "")
    apply_link = job.get("apply_link", "")
    salary = job.get("salary", "")
    is_priority = job.get("is_priority", False)
    
    try:
        success = await notifier.send_job_notification(
            job_title=title,
            company_name=company,
            location=location,
            salary=salary,
            job_url=job_url,
            apply_email=apply_email,
            apply_link=apply_link,
            platform=platform,
            is_priority=is_priority,
        )
        if success:
            logger.info("Job sent to Telegram", title=title[:30])
        return success
    except Exception as e:
        logger.error("Failed to send to Telegram", error=str(e))
        return False


async def is_job_already_sent(job_url: str) -> bool:
    """Check if job was already sent to avoid duplicates"""
    if not job_url:
        return False
    try:
        async for session in get_async_session():
            result = await session.execute(
                select(Job).where(Job.job_url == job_url).limit(1)
            )
            existing = result.scalar_one_or_none()
            return existing is not None
    except Exception as e:
        logger.error("Error checking duplicate", error=str(e))
        return False


async def save_job_to_db(job: dict) -> bool:
    """Save job to database"""
    try:
        async for session in get_async_session():
            job_record = Job(
                job_title=job.get("job_title"),
                company_name=job.get("company_name"),
                location=job.get("location"),
                description=job.get("description", ""),
                salary=job.get("salary"),
                job_url=job.get("job_url"),
                source_platform=job.get("source_platform"),
                apply_email=job.get("apply_email"),
                apply_link=job.get("apply_link"),
            )
            session.add(job_record)
            await session.commit()
            return True
    except Exception as e:
        logger.error("Failed to save job", error=str(e))
        return False


async def main():
    print("=" * 60)
    print("🎯 JOB FINDER - Auto Scrape & Telegram Notify")
    print("=" * 60)
    print()
    
    scraper = LocalJobScraper()
    notifier = TelegramNotifier()
    
    total_found = 0
    total_new = 0
    total_sent = 0
    
    # Get keywords from config
    keywords = JOB_KEYWORDS[:3]  # Limit to first 3 keywords for speed
    
    print(f"🔍 Searching for {len(keywords)} keywords...")
    print(f"Keywords: {', '.join(keywords)}")
    print()
    
    try:
        for keyword_idx, keyword in enumerate(keywords, 1):
            print(f"[{keyword_idx}/{len(keywords)}] Searching: {keyword}")
            print(f"  Platforms: LinkedIn, JobStreet, Glints, Kalibrr")
            
            try:
                # Scrape this keyword from ALL platforms
                jobs = await scraper.scrape(keyword)
                total_found += len(jobs)
                
                # Count by platform
                platform_counts = {}
                for job in jobs:
                    platform = job.get("source_platform", "unknown")
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                print(f"  Found {len(jobs)} jobs total:")
                for platform, count in platform_counts.items():
                    print(f"    - {platform.title()}: {count}")
                
                # Process each job immediately
                for job in jobs:
                    job_url = job.get("job_url", "")
                    title = job.get("job_title", "Unknown")[:40]
                    
                    # Check if already sent
                    if job_url and await is_job_already_sent(job_url):
                        print(f"  ⏭️  Already sent: {title}")
                        continue
                    
                    total_new += 1
                    
                    # Send to Telegram
                    success = await send_job_to_telegram(notifier, job)
                    
                    if success:
                        total_sent += 1
                        print(f"  ✅ Sent: {title}")
                        
                        # Save to database
                        await save_job_to_db(job)
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(1)
                    else:
                        print(f"  ❌ Failed: {title}")
                
                print()
                
            except Exception as e:
                logger.error("Keyword scrape failed", keyword=keyword, error=str(e))
                print(f"  ❌ Error: {e}\n")
        
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total found: {total_found}")
        print(f"New jobs: {total_new}")
        print(f"Sent to Telegram: {total_sent}")
        print("=" * 60)
        
        # Send summary to Telegram
        if total_sent > 0:
            summary = (
                f"✅ <b>Job Search Complete</b>\n\n"
                f"🔍 Total found: {total_found}\n"
                f"🆕 New jobs: {total_new}\n"
                f"📱 Sent to Telegram: {total_sent}\n\n"
                f"Keywords: {', '.join(keywords)}"
            )
            await notifier.send_message(summary)
        
    except Exception as e:
        logger.error("Job finder error", error=str(e))
        print(f"❌ Error: {e}")
        
        # Notify error
        await notifier.notify_error("Job Finder", str(e))


if __name__ == "__main__":
    asyncio.run(main())
