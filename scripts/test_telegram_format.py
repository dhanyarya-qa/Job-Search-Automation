"""
Test Telegram message format with all fields
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.notifications.telegram_notifier import TelegramNotifier
from datetime import datetime, timezone, timedelta

async def test_complete_message():
    print("=" * 60)
    print("Testing Complete Telegram Message Format")
    print("=" * 60)
    
    notifier = TelegramNotifier()
    
    # Create a test job with ALL fields
    test_job = {
        "job_title": "Senior Backend Engineer (Remote)",
        "company_name": "Tokopedia",
        "location": "Jakarta, Indonesia",
        "salary": "Rp 15-25 juta per bulan",
        "job_url": "https://www.linkedin.com/jobs/view/123456",
        "apply_email": "careers@tokopedia.com",
        "apply_link": "https://www.tokopedia.com/careers/apply/123",
        "source_platform": "linkedin",
        "is_priority": True,
        "description": "We are looking for a Senior Backend Engineer to join our team. You will work with Go, PostgreSQL, Redis, and Kafka. Must have 5+ years of experience in backend development. This is a full-time remote position with competitive salary and benefits.",
        "job_type": "Full-time",
        "experience_level": "Senior",
        "is_remote": True,
        "posted_date": datetime.now(timezone.utc) - timedelta(days=2),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=28),
    }
    
    print("\nSending test job to Telegram...")
    print(f"Title: {test_job['job_title']}")
    print(f"Company: {test_job['company_name']}")
    print(f"Type: {test_job['job_type']}")
    print(f"Level: {test_job['experience_level']}")
    print(f"Remote: {test_job['is_remote']}")
    print(f"Priority: {test_job['is_priority']}")
    print()
    
    success = await notifier.send_job_notification(
        job_title=test_job["job_title"],
        company_name=test_job["company_name"],
        location=test_job["location"],
        salary=test_job["salary"],
        job_url=test_job["job_url"],
        apply_email=test_job["apply_email"],
        apply_link=test_job["apply_link"],
        platform=test_job["source_platform"],
        is_priority=test_job["is_priority"],
        description=test_job["description"],
        job_type=test_job["job_type"],
        experience_level=test_job["experience_level"],
        is_remote=test_job["is_remote"],
        posted_date=test_job["posted_date"],
        expires_at=test_job["expires_at"],
    )
    
    if success:
        print("✅ Message sent successfully!")
        print("\nCheck your Telegram to verify the message shows:")
        print("  ✓ Job title")
        print("  ✓ Company name")
        print("  ✓ Location")
        print("  ✓ Salary")
        print("  ✓ Job Type (Full-time)")
        print("  ✓ Experience Level (Senior)")
        print("  ✓ Remote status (Yes)")
        print("  ✓ Platform (LinkedIn)")
        print("  ✓ Posted date")
        print("  ✓ Expiry date")
        print("  ✓ Description preview")
        print("  ✓ Apply email")
        print("  ✓ Apply link")
        print("  ✓ Action buttons")
    else:
        print("❌ Failed to send message")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(test_complete_message())
    sys.exit(0 if result else 1)
