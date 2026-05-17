"""
Simple Job Finder - Scrape jobs and immediately send to Telegram
No AI scoring, just find and notify
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.scraper.local_scraper import LocalJobScraper
from app.notifications.telegram_notifier import TelegramNotifier
from app.database.session import get_async_session
from app.database.models.job import Job
from sqlalchemy import select

logger = structlog.get_logger(__name__)


async def send_job_to_telegram(notifier: TelegramNotifier, job: dict) -> bool:
    """Send job notification to Telegram with apply info"""
    
    # Format job message
    title = job.get("job_title", "Unknown Position")
    company = job.get("company_name", "Unknown Company")
    location = job.get("location", "Location not specified")
    platform = job.get("source_platform", "").title()
    job_url = job.get("job_url", "")
    apply_email = job.get("apply_email", "")
    apply_link = job.get("apply_link", "")
    salary = job.get("salary", "")
    
    # Build message
    message = f"🎯 <b>New Job Found!</b>\n\n"
    message += f"📋 <b>{title}</b>\n"
    message += f"🏢 {company}\n"
    message += f"📍 {location}\n"
    
    if salary:
        message += f"💰 {salary}\n"
    
    message += f"🌐 Platform: {platform}\n\n"
    
    # Add apply information
    message += "<b>📨 How to Apply:</b>\n"
    
    if apply_email:
        message += f"✉️ Email: <code>{apply_email}</code>\n"
    
    if apply_link:
        message += f"🔗 Apply: {apply_link}\n"
    elif job_url:
        message += f"🔗 Job Link: {job_url}\n"
    
    if not apply_email and not apply_link and not job_url:
        message += "ℹ️ Check platform for application details\n"
    
    message += f"\n⏰ Found: {job.get('scraped_at', 'Just now')}"
    
    try:
        success = await notifier.send_message(message)
        if success:
            logger.info("Job sent to Telegram", title=title, company=company)
        return success
    except Exception as e:
        logger.error("Failed to send to Telegram", error=str(e))
        return False


async def is_job_already_sent(job_url: str) -> bool:
    """Check if job was already sent to avoid duplicates.
    
    Normalizes URL to strip tracking params that change per session.
    """
    try:
        from app.scraper.extractor import JobExtractor
        normalized_url = JobExtractor.normalize_job_url(job_url)
        
        async for session in get_async_session():
            result = await session.execute(
                select(Job).where(Job.job_url == normalized_url).limit(1)
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
            logger.info("Job saved to database", title=job.get("job_title"))
            return True
    except Exception as e:
        logger.error("Failed to save job", error=str(e))
        return False


async def main():
    print("=" * 60)
    print("🎯 JOB FINDER - Auto Scrape & Telegram Notify")
    print("=" * 60)
    print()
    
    # Initialize
    scraper = LocalJobScraper()
    notifier = TelegramNotifier()
    
    print("🔍 Starting job search...")
    print()
    
    try:
        # Scrape all keywords
        jobs = await scraper.scrape_all_keywords()
        
        print(f"✅ Found {len(jobs)} jobs total")
        print()
        
        if not jobs:
            print("⚠️  No jobs found. Try again later.")
            return
        
        # Process each job
        new_jobs = 0
        sent_jobs = 0
        skipped_jobs = 0
        
        for i, job in enumerate(jobs, 1):
            job_url = job.get("job_url", "")
            title = job.get("job_title", "Unknown")
            
            print(f"[{i}/{len(jobs)}] Processing: {title[:50]}...")
            
            # Check if already sent
            if job_url and await is_job_already_sent(job_url):
                print(f"  ⏭️  Already sent, skipping")
                skipped_jobs += 1
                continue
            
            new_jobs += 1
            
            # Send to Telegram
            success = await send_job_to_telegram(notifier, job)
            
            if success:
                sent_jobs += 1
                print(f"  ✅ Sent to Telegram")
                
                # Save to database
                await save_job_to_db(job)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
            else:
                print(f"  ❌ Failed to send")
        
        print()
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total found: {len(jobs)}")
        print(f"Already sent: {skipped_jobs}")
        print(f"New jobs: {new_jobs}")
        print(f"Sent to Telegram: {sent_jobs}")
        print("=" * 60)
        
        # Send summary to Telegram
        if sent_jobs > 0:
            summary = (
                f"✅ <b>Job Search Complete</b>\n\n"
                f"🔍 Total found: {len(jobs)}\n"
                f"🆕 New jobs: {new_jobs}\n"
                f"📱 Sent to Telegram: {sent_jobs}"
            )
            await notifier.send_message(summary)
        
    except Exception as e:
        logger.error("Job finder error", error=str(e))
        print(f"❌ Error: {e}")
        
        # Notify error
        await notifier.notify_error("Job Finder", str(e))


if __name__ == "__main__":
    asyncio.run(main())
