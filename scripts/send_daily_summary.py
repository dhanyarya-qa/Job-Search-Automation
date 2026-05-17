"""
Daily Summary - Send daily job statistics to Telegram
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.database.session import get_async_session
from app.database.models.job import Job
from app.notifications.telegram_notifier import TelegramNotifier


async def get_daily_stats():
    """Get daily job statistics"""
    async for session in get_async_session():
        # Total jobs
        total_result = await session.execute(select(func.count(Job.id)))
        total_jobs = total_result.scalar()
        
        # New jobs today
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        new_result = await session.execute(
            select(func.count(Job.id)).where(Job.created_at >= today)
        )
        new_jobs = new_result.scalar()
        
        # Top companies (last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        companies_result = await session.execute(
            select(Job.company_name, func.count(Job.id).label('count'))
            .where(Job.created_at >= week_ago)
            .group_by(Job.company_name)
            .order_by(func.count(Job.id).desc())
            .limit(5)
        )
        top_companies = [row[0] for row in companies_result.all()]
        
        # Jobs by platform
        platforms_result = await session.execute(
            select(Job.source_platform, func.count(Job.id).label('count'))
            .where(Job.created_at >= week_ago)
            .group_by(Job.source_platform)
        )
        platforms = {row[0]: row[1] for row in platforms_result.all()}
        
        return {
            'total_jobs': total_jobs,
            'new_jobs': new_jobs,
            'top_companies': top_companies,
            'platforms': platforms,
        }


async def main():
    print("📊 Generating daily summary...")
    
    try:
        stats = await get_daily_stats()
        
        notifier = TelegramNotifier()
        success = await notifier.notify_daily_summary(
            total_jobs=stats['total_jobs'],
            new_jobs=stats['new_jobs'],
            top_companies=stats['top_companies'],
            top_platforms=stats['platforms'],
        )
        
        if success:
            print("✅ Daily summary sent to Telegram")
        else:
            print("❌ Failed to send daily summary")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
