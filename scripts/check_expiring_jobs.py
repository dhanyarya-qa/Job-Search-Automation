"""
Job Expiry Reminder - Notify about jobs expiring soon
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database.session import get_async_session
from app.database.models.job import Job
from app.notifications.telegram_notifier import TelegramNotifier


async def check_expiring_jobs():
    """Check for jobs expiring in next 3 days"""
    notifier = TelegramNotifier()
    
    async for session in get_async_session():
        now = datetime.now(timezone.utc)
        three_days = now + timedelta(days=3)
        
        # Find jobs expiring soon
        result = await session.execute(
            select(Job)
            .where(
                Job.expires_at.isnot(None),
                Job.expires_at <= three_days,
                Job.expires_at > now,
                Job.is_active == True,
            )
            .order_by(Job.expires_at)
        )
        expiring_jobs = result.scalars().all()
        
        print(f"Found {len(expiring_jobs)} jobs expiring soon")
        
        for job in expiring_jobs:
            days_left = (job.expires_at - now).days
            
            await notifier.notify_job_expiring(
                job_title=job.job_title,
                company=job.company_name,
                days_left=days_left,
                job_url=job.job_url,
            )
            
            await asyncio.sleep(1)  # Rate limit
        
        return len(expiring_jobs)


async def main():
    print("⏰ Checking for expiring jobs...")
    
    try:
        count = await check_expiring_jobs()
        print(f"✅ Sent {count} expiry reminders")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
