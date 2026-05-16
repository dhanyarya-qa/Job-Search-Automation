"""Test Telegram notification"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from app.notifications.telegram_notifier import TelegramNotifier
from app.config import settings

async def main():
    print("🔔 Testing Telegram Notification...")
    print(f"📱 Bot Token: {settings.telegram_bot_token[:20]}...")
    print(f"💬 Chat ID: {settings.telegram_chat_id}")
    
    notifier = TelegramNotifier()
    
    # Test job data
    test_job = {
        "job_title": "QA Automation Engineer",
        "company_name": "Tech Corp Indonesia",
        "location": "Jakarta",
        "salary": "Rp 10-15 juta",
        "job_url": "https://example.com/jobs/qa-engineer",
        "apply_email": "recruitment@techcorp.com",
        "apply_link": "https://careers.techcorp.com/apply/12345",
        "description": "Looking for QA Engineer with Playwright and Python experience",
        "source_platform": "LinkedIn"
    }
    
    # Test AI analysis result
    test_analysis = {
        "match_score": 95,
        "reasoning": "Excellent match! Strong alignment with Playwright automation and Python skills. Company is looking for exactly your expertise.",
        "job_category": "QA Automation",
        "confidence": 0.95,
        "prediction_market": "🚀 Elite Match (95%+ Win Rate)"
    }
    
    try:
        # Test 1: Send simple message
        print("\n📤 Test 1: Sending simple message...")
        success = await notifier.send_message("🤖 Test notification from Ultimate Job Hunting ATS!")
        if success:
            print("✅ Simple message sent!")
        
        # Test 2: Send job alert
        print("\n📤 Test 2: Sending job alert...")
        success = await notifier.notify_new_job(
            job_title=test_job["job_title"],
            company_name=test_job["company_name"],
            match_score=test_analysis["match_score"],
            prediction_market=test_analysis["prediction_market"],
            job_url=test_job["job_url"]
        )
        if success:
            print("✅ Job alert sent!")
        
        # Test 3: Send scrape complete notification
        print("\n📤 Test 3: Sending scrape complete notification...")
        success = await notifier.notify_scrape_complete(jobs_found=25, jobs_saved=10)
        if success:
            print("✅ Scrape complete notification sent!")
        
        print("\n✅ All notifications sent successfully!")
        print("📱 Check your Telegram app for 3 messages")
        
    except Exception as e:
        print(f"\n❌ Error sending notification: {e}")
        print("\nTroubleshooting:")
        print("1. Check TELEGRAM_BOT_TOKEN is correct")
        print("2. Check TELEGRAM_CHAT_ID is correct")
        print("3. Make sure bot is started (send /start to bot)")
        print("4. Make sure bot has permission to send messages")

if __name__ == "__main__":
    asyncio.run(main())
