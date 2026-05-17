"""
Quick test - scrape one keyword from one platform and send to Telegram
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scraper.local_scraper import LocalJobScraper
from app.notifications.telegram_notifier import TelegramNotifier


async def send_job_to_telegram(notifier: TelegramNotifier, job: dict) -> bool:
    """Send job notification to Telegram"""
    
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
        message += "ℹ️ Check platform for details\n"
    
    try:
        return await notifier.send_message(message)
    except Exception as e:
        print(f"Error sending: {e}")
        return False


async def main():
    print("🎯 Quick Job Finder Test - All Platforms\n")
    
    scraper = LocalJobScraper()
    notifier = TelegramNotifier()
    
    # Test with one keyword but ALL platforms
    keyword = "QA Engineer"
    print(f"Searching for: {keyword}")
    print("Platforms: LinkedIn, JobStreet, Glints, Kalibrr\n")
    
    try:
        # scrape() already searches ALL platforms
        jobs = await scraper.scrape(keyword)
        
        print(f"\n✅ Found {len(jobs)} jobs total from all platforms\n")
        
        if jobs:
            # Send ALL jobs to Telegram
            sent = 0
            failed = 0
            
            for i, job in enumerate(jobs, 1):
                title = job.get("job_title", "Unknown")
                platform = job.get("source_platform", "").title()
                print(f"[{i}/{len(jobs)}] {platform} - {title[:40]}...")
                
                success = await send_job_to_telegram(notifier, job)
                
                if success:
                    sent += 1
                    print(f"    ✅ Sent!")
                else:
                    failed += 1
                    print(f"    ❌ Failed")
                
                await asyncio.sleep(1)  # Delay to avoid rate limit
            
            print(f"\n✅ Test complete!")
            print(f"   Total: {len(jobs)} jobs")
            print(f"   Sent: {sent}")
            print(f"   Failed: {failed}")
        else:
            print("⚠️  No jobs found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
