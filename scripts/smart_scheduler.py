"""
Smart Scheduler - Different scraping frequencies per platform
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.scraper.local_scraper import LocalJobScraper
from app.scraper.filters import JobFilter, DEFAULT_FILTER
from app.notifications.telegram_notifier import TelegramNotifier
from app.database.session import get_async_session
from app.database.models.job import Job
from sqlalchemy import select
from app.scraper.constants import JOB_KEYWORDS

logger = structlog.get_logger(__name__)

# Platform scheduling config (in hours)
PLATFORM_SCHEDULE = {
    "linkedin": 2,      # Every 2 hours (high priority)
    "jobstreet": 3,     # Every 3 hours
    "glints": 4,        # Every 4 hours
    "kalibrr": 4,       # Every 4 hours
    "indeed": 6,        # Every 6 hours
    "karir": 8,         # Every 8 hours
    "urbanhire": 12,    # Every 12 hours
}

SCHEDULE_FILE = "outputs/last_scrape_times.json"


def load_last_scrape_times():
    """Load last scrape times from file"""
    try:
        if Path(SCHEDULE_FILE).exists():
            with open(SCHEDULE_FILE, "r") as f:
                data = json.load(f)
                # Convert string timestamps back to datetime
                return {k: datetime.fromisoformat(v) for k, v in data.items()}
    except Exception as e:
        logger.error("Failed to load schedule", error=str(e))
    return {}


def save_last_scrape_times(times: dict):
    """Save last scrape times to file"""
    try:
        Path(SCHEDULE_FILE).parent.mkdir(parents=True, exist_ok=True)
        # Convert datetime to string for JSON
        data = {k: v.isoformat() for k, v in times.items()}
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error("Failed to save schedule", error=str(e))


def should_scrape_platform(platform: str, last_scrape_times: dict) -> bool:
    """Check if platform should be scraped based on schedule"""
    if platform not in PLATFORM_SCHEDULE:
        return True  # Unknown platforms always scrape
    
    if platform not in last_scrape_times:
        return True  # Never scraped before
    
    last_scrape = last_scrape_times[platform]
    hours_since = (datetime.now(timezone.utc) - last_scrape).total_seconds() / 3600
    required_hours = PLATFORM_SCHEDULE[platform]
    
    return hours_since >= required_hours


async def is_job_already_sent(job_url: str) -> bool:
    """Check if job was already sent"""
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
                job_type=job.get("job_type"),
                experience_level=job.get("experience_level"),
                is_remote=job.get("is_remote", False),
                is_priority=job.get("is_priority", False),
                expires_at=job.get("expires_at"),
                sent_to_telegram=True,
                telegram_sent_at=datetime.now(timezone.utc),
            )
            session.add(job_record)
            await session.commit()
            return True
    except Exception as e:
        logger.error("Failed to save job", error=str(e))
        return False


async def main():
    print("=" * 60)
    print("🤖 SMART SCHEDULER - Platform-Specific Scraping")
    print("=" * 60)
    print()
    
    # Load last scrape times
    last_scrape_times = load_last_scrape_times()
    
    # Check which platforms to scrape
    platforms_to_scrape = []
    for platform, interval in PLATFORM_SCHEDULE.items():
        if should_scrape_platform(platform, last_scrape_times):
            platforms_to_scrape.append(platform)
            print(f"✅ {platform.title()}: Ready to scrape (interval: {interval}h)")
        else:
            last_scrape = last_scrape_times[platform]
            hours_since = (datetime.now(timezone.utc) - last_scrape).total_seconds() / 3600
            print(f"⏭️  {platform.title()}: Skipping (last scraped {hours_since:.1f}h ago, interval: {interval}h)")
    
    if not platforms_to_scrape:
        print("\n⏸️  No platforms need scraping at this time")
        return
    
    print(f"\n🎯 Scraping {len(platforms_to_scrape)} platforms: {', '.join(platforms_to_scrape)}")
    print()
    
    scraper = LocalJobScraper()
    notifier = TelegramNotifier()
    job_filter = DEFAULT_FILTER
    
    total_found = 0
    total_sent = 0
    
    keywords = JOB_KEYWORDS[:3]
    
    try:
        for keyword in keywords:
            print(f"🔍 Keyword: {keyword}")
            
            for platform in platforms_to_scrape:
                try:
                    # Scrape this platform
                    from app.scraper.constants import LOCAL_PLATFORMS
                    url_template = LOCAL_PLATFORMS.get(platform)
                    
                    if not url_template:
                        continue
                    
                    url = url_template.format(keyword=keyword.replace(" ", "+"))
                    
                    await scraper.initialize_browser()
                    jobs = await scraper._scrape_platform(platform, url)
                    await scraper.close()
                    
                    total_found += len(jobs)
                    print(f"  {platform.title()}: {len(jobs)} jobs")
                    
                    # Apply filters
                    filtered_jobs, priority_jobs = job_filter.filter_jobs(jobs)
                    all_filtered = priority_jobs + filtered_jobs
                    
                    # Send to Telegram
                    for job in all_filtered:
                        job_url = job.get("job_url", "")
                        
                        if job_url and await is_job_already_sent(job_url):
                            continue
                        
                        # Send notification
                        success = await notifier.send_job_notification(
                            job_title=job.get("job_title", ""),
                            company_name=job.get("company_name", ""),
                            location=job.get("location", ""),
                            salary=job.get("salary", ""),
                            job_url=job_url,
                            apply_email=job.get("apply_email", ""),
                            apply_link=job.get("apply_link", ""),
                            platform=platform,
                            is_priority=job.get("is_priority", False),
                        )
                        
                        if success:
                            total_sent += 1
                            await save_job_to_db(job)
                            await asyncio.sleep(1)
                    
                    # Update last scrape time for this platform
                    last_scrape_times[platform] = datetime.now(timezone.utc)
                    
                except Exception as e:
                    logger.error("Platform scrape failed", platform=platform, error=str(e))
            
            print()
        
        # Save updated scrape times
        save_last_scrape_times(last_scrape_times)
        
        print("=" * 60)
        print(f"📊 Total found: {total_found}")
        print(f"📱 Sent to Telegram: {total_sent}")
        print("=" * 60)
        
        # Send summary
        if total_sent > 0:
            summary = (
                f"✅ <b>Smart Scheduler Complete</b>\n\n"
                f"🔍 Platforms scraped: {len(platforms_to_scrape)}\n"
                f"📦 Total found: {total_found}\n"
                f"📱 Sent: {total_sent}\n\n"
                f"Platforms: {', '.join([p.title() for p in platforms_to_scrape])}"
            )
            await notifier.send_message(summary)
        
    except Exception as e:
        logger.error("Smart scheduler error", error=str(e))
        await notifier.notify_error("Smart Scheduler", str(e))


if __name__ == "__main__":
    asyncio.run(main())
