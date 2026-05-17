"""
Test scraping one job and sending to Telegram with all fields
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scraper.local_scraper import LocalJobScraper
from app.notifications.telegram_notifier import TelegramNotifier
from app.scraper.filters import DEFAULT_FILTER

async def main():
    print("=" * 60)
    print("Testing Complete Pipeline: Scrape → Filter → Telegram")
    print("=" * 60)
    
    scraper = LocalJobScraper()
    notifier = TelegramNotifier()
    job_filter = DEFAULT_FILTER
    
    # Scrape just one keyword from LinkedIn
    keyword = "software engineer"
    print(f"\n🔍 Scraping: {keyword}")
    print(f"Platform: LinkedIn")
    
    try:
        jobs = await scraper.scrape(keyword)
        print(f"✅ Found {len(jobs)} jobs")
        
        if not jobs:
            print("❌ No jobs found")
            return
        
        # Show first job details
        first_job = jobs[0]
        print("\n📋 First Job Details:")
        print(f"  Title: {first_job.get('job_title', 'N/A')}")
        print(f"  Company: {first_job.get('company_name', 'N/A')}")
        print(f"  Location: {first_job.get('location', 'N/A')}")
        print(f"  Salary: {first_job.get('salary', 'N/A')}")
        print(f"  Job Type: {first_job.get('job_type', 'N/A')}")
        print(f"  Experience Level: {first_job.get('experience_level', 'N/A')}")
        print(f"  Is Remote: {first_job.get('is_remote', False)}")
        print(f"  Platform: {first_job.get('source_platform', 'N/A')}")
        print(f"  Description: {first_job.get('description', 'N/A')[:100]}...")
        
        # Apply filters
        filtered_jobs, priority_jobs = job_filter.filter_jobs(jobs)
        all_filtered = priority_jobs + filtered_jobs
        
        print(f"\n✨ After filtering: {len(all_filtered)} jobs ({len(priority_jobs)} priority)")
        
        if not all_filtered:
            print("❌ All jobs filtered out")
            return
        
        # Send first filtered job to Telegram
        test_job = all_filtered[0]
        print(f"\n📱 Sending to Telegram...")
        print(f"  Title: {test_job.get('job_title', 'N/A')[:50]}")
        
        success = await notifier.send_job_notification(
            job_title=test_job.get("job_title", ""),
            company_name=test_job.get("company_name", ""),
            location=test_job.get("location", ""),
            salary=test_job.get("salary"),
            job_url=test_job.get("job_url", ""),
            apply_email=test_job.get("apply_email"),
            apply_link=test_job.get("apply_link"),
            platform=test_job.get("source_platform", ""),
            is_priority=test_job.get("is_priority", False),
            description=test_job.get("description"),
            job_type=test_job.get("job_type"),
            experience_level=test_job.get("experience_level"),
            is_remote=test_job.get("is_remote", False),
            posted_date=test_job.get("posted_date"),
            expires_at=test_job.get("expires_at"),
        )
        
        if success:
            print("✅ Message sent to Telegram!")
            print("\n🎯 Check your Telegram to verify all fields are displayed:")
            print("  • Job Type (Full-time/Contract/etc)")
            print("  • Experience Level (Junior/Mid/Senior)")
            print("  • Remote status")
            print("  • Description preview")
            print("  • All other fields")
        else:
            print("❌ Failed to send to Telegram")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
