"""
Test sending a complete job message with all database fields
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.notifications.telegram_notifier import TelegramNotifier


async def test_complete_job_message():
    """Test sending a complete job notification with all fields"""
    print("=" * 60)
    print("📱 TESTING COMPLETE JOB MESSAGE")
    print("=" * 60)
    print()
    
    notifier = TelegramNotifier()
    
    # Sample job data with ALL database fields
    job_data = {
        "job_title": "Senior QA Engineer",
        "company_name": "Tokopedia",
        "location": "Jakarta, Indonesia",
        "salary": "15-20 juta/bulan",
        "job_url": "https://www.linkedin.com/jobs/view/123456789",
        "apply_email": "careers@tokopedia.com",
        "apply_link": "https://careers.tokopedia.com/apply/123",
        "platform": "LinkedIn",
        "is_priority": True,
        "description": """We are looking for an experienced Senior QA Engineer to join our team. 
You will be responsible for:
- Designing and implementing test automation frameworks
- Leading QA team and mentoring junior engineers
- Ensuring product quality across web and mobile platforms
- Working with cross-functional teams to deliver high-quality products

Requirements:
- 5+ years of experience in QA/Testing
- Strong knowledge of automation tools (Selenium, Playwright, Appium)
- Experience with API testing (Postman, REST Assured)
- Excellent problem-solving and communication skills""",
        "job_type": "Full-time",
        "experience_level": "Senior",
        "is_remote": True,
        "posted_date": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=30),
    }
    
    print("📤 Sending complete job message...")
    print(f"   Title: {job_data['job_title']}")
    print(f"   Company: {job_data['company_name']}")
    print(f"   Priority: {'Yes' if job_data['is_priority'] else 'No'}")
    print()
    
    success = await notifier.send_job_notification(
        job_title=job_data["job_title"],
        company_name=job_data["company_name"],
        location=job_data["location"],
        salary=job_data["salary"],
        job_url=job_data["job_url"],
        apply_email=job_data["apply_email"],
        apply_link=job_data["apply_link"],
        platform=job_data["platform"],
        is_priority=job_data["is_priority"],
        description=job_data["description"],
        job_type=job_data["job_type"],
        experience_level=job_data["experience_level"],
        is_remote=job_data["is_remote"],
        posted_date=job_data["posted_date"],
        expires_at=job_data["expires_at"],
    )
    
    if success:
        print("✅ Complete job message sent successfully!")
        print()
        print("Check your:")
        print("1. Personal chat with bot")
        print("2. Channel: https://t.me/+wchyhkrRqJoyMGM9")
        print()
        print("You should see:")
        print("✅ Job title, company, location")
        print("✅ Salary, job type, experience level")
        print("✅ Remote status")
        print("✅ Posted date & expiry date")
        print("✅ Description preview (first 200 chars)")
        print("✅ Apply email & link")
        print("✅ Inline buttons (Apply, Save, Not Interested, Company Info)")
    else:
        print("❌ Failed to send message")


if __name__ == "__main__":
    asyncio.run(test_complete_job_message())
