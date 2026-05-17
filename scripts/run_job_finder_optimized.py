"""
Optimized Job Finder - Fast scraping with immediate Telegram notifications
Scrapes:
1. LinkedIn Jobs (from job search)
2. LinkedIn Posts (from feed/posts about jobs)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.scraper.local_scraper import LocalJobScraper
from app.scraper.linkedin_post_scraper import LinkedInPostScraper
from app.scraper.filters import JobFilter, DEFAULT_FILTER
from app.notifications.telegram_notifier import TelegramNotifier
from app.database.session import get_async_session
from app.database.models.job import Job
from sqlalchemy import select
from app.scraper.constants import JOB_KEYWORDS
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)


async def send_job_to_telegram(notifier: TelegramNotifier, job: dict, is_from_post: bool = False) -> bool:
    """Send job notification to Telegram with apply info and buttons"""
    
    title = job.get("job_title", "Unknown Position")
    company = job.get("company_name", "Unknown Company")
    location = job.get("location", "Location not specified")
    platform = job.get("source_platform", "")
    
    # Add "Postingan" label if from LinkedIn post
    if is_from_post:
        platform = f"📮 Postingan - {platform}"
    
    job_url = job.get("job_url", "")
    apply_email = job.get("apply_email", "")
    apply_link = job.get("apply_link", "")
    salary = job.get("salary", "")
    is_priority = job.get("is_priority", False)
    description = job.get("description", "")
    job_type = job.get("job_type", "")
    experience_level = job.get("experience_level", "")
    is_remote = job.get("is_remote", False)
    posted_date = job.get("posted_date")
    expires_at = job.get("expires_at")
    
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
            description=description,
            job_type=job_type,
            experience_level=experience_level,
            is_remote=is_remote,
            posted_date=posted_date,
            expires_at=expires_at,
        )
        if success:
            logger.info("Job sent to Telegram", title=title[:30], is_post=is_from_post)
        return success
    except Exception as e:
        logger.error("Failed to send to Telegram", error=str(e))
        return False


async def save_job_to_db_with_tracking(job: dict) -> bool:
    """Save job to database with Telegram tracking"""
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


async def is_job_already_sent(job_url: str) -> bool:
    """Check if job was already sent to avoid duplicates.
    
    Normalizes URL first to strip tracking params (position, refId, etc.)
    that LinkedIn/Indeed append differently on each scrape session.
    """
    if not job_url:
        return False
    
    from app.scraper.extractor import JobExtractor
    normalized_url = JobExtractor.normalize_job_url(job_url)
    
    try:
        async for session in get_async_session():
            result = await session.execute(
                select(Job).where(Job.job_url == normalized_url).limit(1)
            )
            existing = result.scalar_one_or_none()
            return existing is not None
    except Exception as e:
        logger.error("Error checking duplicate", error=str(e))
        return False





async def main():
    print("=" * 60)
    print("🎯 JOB FINDER - Auto Scrape & Telegram Notify")
    print("=" * 60)
    print()
    
    job_scraper = LocalJobScraper()
    post_scraper = LinkedInPostScraper()
    notifier = TelegramNotifier()
    job_filter = DEFAULT_FILTER
    
    total_found = 0
    total_filtered = 0
    total_new = 0
    total_sent = 0
    
    total_posts_found = 0
    total_posts_filtered = 0
    total_posts_new = 0
    total_posts_sent = 0
    
    # Get keywords from config
    keywords = JOB_KEYWORDS[:3]  # Limit to first 3 keywords for speed
    
    print(f"🔍 Searching for {len(keywords)} keywords...")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Sources: LinkedIn Jobs + Indeed + Dealls + LinkedIn Posts")
    print()
    
    try:
        for keyword_idx, keyword in enumerate(keywords, 1):
            print(f"[{keyword_idx}/{len(keywords)}] Searching: {keyword}")
            print(f"  Platforms: LinkedIn Jobs, Indeed, Dealls, LinkedIn Posts")
            
            # ===== 1. SCRAPE LINKEDIN JOBS & INDEED =====
            try:
                jobs = await job_scraper.scrape(keyword)
                total_found += len(jobs)
                
                # Count by platform
                platform_counts = {}
                for job in jobs:
                    platform = job.get("source_platform", "unknown")
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                print(f"  📋 Jobs found: {len(jobs)}")
                for platform, count in platform_counts.items():
                    print(f"    - {platform.title()}: {count}")
                
                # Apply filters
                filtered_jobs, priority_jobs = job_filter.filter_jobs(jobs)
                all_filtered = priority_jobs + filtered_jobs
                total_filtered += len(all_filtered)
                
                print(f"  ✨ After filtering: {len(all_filtered)} jobs ({len(priority_jobs)} priority)")
                
                # Send jobs to Telegram
                for job in all_filtered:
                    job_url = job.get("job_url", "")
                    title = job.get("job_title", "Unknown")[:40]
                    
                    if job_url and await is_job_already_sent(job_url):
                        print(f"    ⏭️  Already sent: {title}")
                        continue
                    
                    total_new += 1
                    
                    success = await send_job_to_telegram(notifier, job, is_from_post=False)
                    
                    if success:
                        total_sent += 1
                        priority_mark = "⭐" if job.get("is_priority") else "✅"
                        print(f"    {priority_mark} Sent: {title}")
                        await save_job_to_db_with_tracking(job)
                        await asyncio.sleep(1)
                    else:
                        print(f"    ❌ Failed: {title}")
                
            except Exception as e:
                logger.error("Job scraping failed", keyword=keyword, error=str(e))
                print(f"  ❌ Job scraping error: {e}")
            
            # ===== 2. SCRAPE LINKEDIN POSTS =====
            try:
                print(f"  📮 Searching LinkedIn posts...")
                posts = await post_scraper.scrape(keyword)
                total_posts_found += len(posts)
                
                print(f"  📮 Posts found: {len(posts)}")
                
                # Apply filters to posts
                filtered_posts, priority_posts = job_filter.filter_jobs(posts)
                all_filtered_posts = priority_posts + filtered_posts
                total_posts_filtered += len(all_filtered_posts)
                
                print(f"  ✨ After filtering: {len(all_filtered_posts)} posts ({len(priority_posts)} priority)")
                
                # Send posts to Telegram
                for post in all_filtered_posts:
                    post_url = post.get("job_url", "")
                    title = post.get("job_title", "Unknown")[:40]
                    
                    if post_url and await is_job_already_sent(post_url):
                        print(f"    ⏭️  Already sent: {title}")
                        continue
                    
                    total_posts_new += 1
                    
                    success = await send_job_to_telegram(notifier, post, is_from_post=True)
                    
                    if success:
                        total_posts_sent += 1
                        priority_mark = "⭐" if post.get("is_priority") else "📮"
                        print(f"    {priority_mark} Sent (Post): {title}")
                        await save_job_to_db_with_tracking(post)
                        await asyncio.sleep(1)
                    else:
                        print(f"    ❌ Failed: {title}")
                
            except Exception as e:
                logger.error("Post scraping failed", keyword=keyword, error=str(e))
                print(f"  ❌ Post scraping error: {e}")
            
            print()
        
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"📋 JOBS (LinkedIn + Indeed + Dealls):")
        print(f"  Total found: {total_found}")
        print(f"  After filters: {total_filtered}")
        print(f"  New jobs: {total_new}")
        print(f"  Sent to Telegram: {total_sent}")
        print()
        print(f"📮 POSTS (LinkedIn Feed):")
        print(f"  Total found: {total_posts_found}")
        print(f"  After filters: {total_posts_filtered}")
        print(f"  New posts: {total_posts_new}")
        print(f"  Sent to Telegram: {total_posts_sent}")
        print()
        print(f"🎯 TOTAL SENT: {total_sent + total_posts_sent}")
        print("=" * 60)
        
        # Send summary to Telegram
        if total_sent > 0 or total_posts_sent > 0:
            summary = (
                f"✅ <b>Job Search Complete</b>\n\n"
                f"📋 <b>Jobs (LinkedIn + Indeed + Dealls)</b>\n"
                f"🔍 Found: {total_found}\n"
                f"✨ Filtered: {total_filtered}\n"
                f"🆕 New: {total_new}\n"
                f"📱 Sent: {total_sent}\n\n"
                f"📮 <b>Posts (LinkedIn Feed)</b>\n"
                f"🔍 Found: {total_posts_found}\n"
                f"✨ Filtered: {total_posts_filtered}\n"
                f"🆕 New: {total_posts_new}\n"
                f"📱 Sent: {total_posts_sent}\n\n"
                f"🎯 <b>Total Sent: {total_sent + total_posts_sent}</b>\n"
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
