"""
Test All Platforms - Debug why only LinkedIn works
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scraper.local_scraper import LocalJobScraper
from app.scraper.constants import LOCAL_PLATFORMS


async def test_platform(scraper, platform, url):
    """Test a single platform"""
    print(f"\n{'='*60}")
    print(f"🔍 Testing: {platform.upper()}")
    print(f"URL: {url[:80]}...")
    print('='*60)
    
    try:
        await scraper.initialize_browser()
        jobs = await scraper._scrape_platform(platform, url)
        await scraper.close()
        
        print(f"✅ Found {len(jobs)} jobs")
        
        if jobs:
            print(f"\n📋 Sample job:")
            job = jobs[0]
            print(f"  Title: {job.get('job_title', 'N/A')}")
            print(f"  Company: {job.get('company_name', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  URL: {job.get('job_url', 'N/A')[:60]}...")
        else:
            print("❌ No jobs found - possible issues:")
            print("  1. Website structure changed")
            print("  2. Anti-bot protection")
            print("  3. Wrong CSS selectors")
            print("  4. Page requires JavaScript rendering")
        
        return len(jobs)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0


async def main():
    print("="*60)
    print("🧪 TESTING ALL PLATFORMS")
    print("="*60)
    
    scraper = LocalJobScraper()
    keyword = "QA Automation"
    
    results = {}
    
    for platform, url_template in LOCAL_PLATFORMS.items():
        url = url_template.format(keyword=keyword.replace(" ", "+"))
        count = await test_platform(scraper, platform, url)
        results[platform] = count
        
        # Small delay between platforms
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for platform, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {platform.title():15} {count:3} jobs")
    
    print("="*60)
    
    working = sum(1 for c in results.values() if c > 0)
    total = len(results)
    print(f"\n✅ Working platforms: {working}/{total}")
    
    if working < total:
        print("\n💡 Recommendation:")
        print("  - Focus on working platforms (LinkedIn)")
        print("  - Update selectors for broken platforms")
        print("  - Or remove broken platforms from scraping")


if __name__ == "__main__":
    asyncio.run(main())
