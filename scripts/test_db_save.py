"""
Test Database Save - Quick test to verify jobs can be saved
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.engine import AsyncSessionLocal
from app.database.models.job import Job


async def test_save():
    """Test saving a job to database"""
    print("=" * 60)
    print("🧪 TESTING DATABASE SAVE")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Create a test job
        test_job = Job(
            id=str(uuid.uuid4()),
            job_title="Test QA Engineer",
            company_name="Test Company",
            location="Jakarta",
            description="Test description",
            salary="10-15 juta",
            source_platform="linkedin",
            job_url="https://test.com/job/123",
            apply_link="https://test.com/apply/123",
            posted_date=datetime.now(),
            expires_at=None,
            job_type="Full-time",
            experience_level="Mid-level",
            is_remote=False,
            is_priority=False,
            is_active=True,
            sent_to_telegram=False,
        )
        
        session.add(test_job)
        await session.commit()
        
        print(f"✅ Job saved: {test_job.job_title}")
        print(f"   ID: {test_job.id}")
        print(f"   Company: {test_job.company_name}")
        print(f"   Location: {test_job.location}")
        
        # Query it back
        from sqlalchemy import select
        result = await session.execute(select(Job).where(Job.id == test_job.id))
        saved_job = result.scalar_one_or_none()
        
        if saved_job:
            print(f"\n✅ Job retrieved from database:")
            print(f"   Title: {saved_job.job_title}")
            print(f"   Has expires_at column: {hasattr(saved_job, 'expires_at')}")
            print(f"   Has sent_to_telegram column: {hasattr(saved_job, 'sent_to_telegram')}")
        else:
            print("\n❌ Job not found in database")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_save())
