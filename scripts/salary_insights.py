"""
Salary Insights - Analyze salary data from scraped jobs
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import structlog
from sqlalchemy import select, func
from app.database.session import get_async_session
from app.database.models.job import Job
from app.notifications.telegram_notifier import TelegramNotifier
from collections import defaultdict

logger = structlog.get_logger(__name__)


def extract_salary_range(salary_text: str) -> tuple[int | None, int | None]:
    """Extract min and max salary from text"""
    if not salary_text:
        return None, None
    
    salary_text = salary_text.lower()
    
    # Remove currency symbols and common words
    salary_text = re.sub(r'(rp|idr|usd|\$|,|\.)', '', salary_text)
    
    # Extract all numbers
    numbers = re.findall(r'\d+', salary_text)
    if not numbers:
        return None, None
    
    # Convert to integers
    nums = [int(n) for n in numbers]
    
    # Handle millions/thousands
    multiplier = 1
    if 'juta' in salary_text or 'million' in salary_text or 'm' in salary_text:
        multiplier = 1_000_000
    elif 'ribu' in salary_text or 'thousand' in salary_text or 'k' in salary_text:
        multiplier = 1_000
    
    nums = [n * multiplier for n in nums]
    
    # Return min and max
    if len(nums) >= 2:
        return min(nums), max(nums)
    elif len(nums) == 1:
        return nums[0], nums[0]
    
    return None, None


async def analyze_salaries():
    """Analyze salary data from database"""
    print("=" * 60)
    print("💰 SALARY INSIGHTS ANALYSIS")
    print("=" * 60)
    print()
    
    async for session in get_async_session():
        # Get all jobs with salary info
        result = await session.execute(
            select(Job).where(Job.salary.isnot(None), Job.salary != "")
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("❌ No salary data found in database")
            return None
        
        print(f"📊 Analyzing {len(jobs)} jobs with salary information...\n")
        
        # Extract salary ranges
        salary_data = []
        by_title = defaultdict(list)
        by_company = defaultdict(list)
        by_platform = defaultdict(list)
        
        for job in jobs:
            min_sal, max_sal = extract_salary_range(job.salary)
            
            if min_sal and max_sal:
                avg_sal = (min_sal + max_sal) / 2
                salary_data.append({
                    "job": job,
                    "min": min_sal,
                    "max": max_sal,
                    "avg": avg_sal,
                })
                
                # Group by title (simplified)
                title_key = job.job_title.lower()
                if "qa" in title_key or "quality" in title_key or "test" in title_key:
                    by_title["QA/Testing"].append(avg_sal)
                elif "engineer" in title_key:
                    by_title["Engineer"].append(avg_sal)
                elif "developer" in title_key or "programmer" in title_key:
                    by_title["Developer"].append(avg_sal)
                else:
                    by_title["Other"].append(avg_sal)
                
                # Group by company
                by_company[job.company_name].append(avg_sal)
                
                # Group by platform
                by_platform[job.source_platform].append(avg_sal)
        
        if not salary_data:
            print("❌ Could not extract salary ranges from data")
            return None
        
        # Calculate overall statistics
        all_salaries = [s["avg"] for s in salary_data]
        overall_avg = sum(all_salaries) / len(all_salaries)
        overall_min = min(all_salaries)
        overall_max = max(all_salaries)
        overall_median = sorted(all_salaries)[len(all_salaries) // 2]
        
        insights = {
            "total_jobs": len(salary_data),
            "overall": {
                "average": overall_avg,
                "median": overall_median,
                "min": overall_min,
                "max": overall_max,
            },
            "by_title": {},
            "by_company": {},
            "by_platform": {},
        }
        
        # Calculate by title
        for title, salaries in by_title.items():
            if salaries:
                insights["by_title"][title] = {
                    "average": sum(salaries) / len(salaries),
                    "count": len(salaries),
                }
        
        # Calculate by company (top 10)
        for company, salaries in sorted(by_company.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            if salaries:
                insights["by_company"][company] = {
                    "average": sum(salaries) / len(salaries),
                    "count": len(salaries),
                }
        
        # Calculate by platform
        for platform, salaries in by_platform.items():
            if salaries:
                insights["by_platform"][platform] = {
                    "average": sum(salaries) / len(salaries),
                    "count": len(salaries),
                }
        
        # Print results
        print("📈 OVERALL STATISTICS")
        print(f"  Average: Rp {insights['overall']['average']:,.0f}")
        print(f"  Median:  Rp {insights['overall']['median']:,.0f}")
        print(f"  Min:     Rp {insights['overall']['min']:,.0f}")
        print(f"  Max:     Rp {insights['overall']['max']:,.0f}")
        print()
        
        print("💼 BY JOB TITLE")
        for title, data in sorted(insights["by_title"].items(), key=lambda x: x[1]["average"], reverse=True):
            print(f"  {title:20} Rp {data['average']:>12,.0f}  ({data['count']} jobs)")
        print()
        
        print("🏢 TOP COMPANIES BY SALARY")
        for company, data in sorted(insights["by_company"].items(), key=lambda x: x[1]["average"], reverse=True)[:5]:
            print(f"  {company[:30]:30} Rp {data['average']:>12,.0f}  ({data['count']} jobs)")
        print()
        
        print("🌐 BY PLATFORM")
        for platform, data in sorted(insights["by_platform"].items(), key=lambda x: x[1]["average"], reverse=True):
            print(f"  {platform.title():15} Rp {data['average']:>12,.0f}  ({data['count']} jobs)")
        print()
        
        print("=" * 60)
        
        return insights


async def send_insights_to_telegram():
    """Analyze salaries and send to Telegram"""
    insights = await analyze_salaries()
    
    if not insights:
        return
    
    notifier = TelegramNotifier()
    
    # Build message
    text = f"💰 <b>Salary Insights Report</b>\n\n"
    text += f"📊 Analyzed {insights['total_jobs']} jobs\n\n"
    
    # Overall stats
    text += f"<b>📈 Overall Statistics</b>\n"
    text += f"Average: Rp {insights['overall']['average']:,.0f}\n"
    text += f"Median:  Rp {insights['overall']['median']:,.0f}\n"
    text += f"Range:   Rp {insights['overall']['min']:,.0f} - Rp {insights['overall']['max']:,.0f}\n\n"
    
    # By title
    text += f"<b>💼 By Job Title</b>\n"
    for title, data in sorted(insights["by_title"].items(), key=lambda x: x[1]["average"], reverse=True):
        text += f"• {title}: Rp {data['average']:,.0f} ({data['count']} jobs)\n"
    text += "\n"
    
    # Top companies
    text += f"<b>🏢 Top 5 Companies</b>\n"
    for company, data in sorted(insights["by_company"].items(), key=lambda x: x[1]["average"], reverse=True)[:5]:
        text += f"• {company[:25]}: Rp {data['average']:,.0f}\n"
    
    await notifier.send_message(text)
    print("\n✅ Insights sent to Telegram!")


async def main():
    await send_insights_to_telegram()


if __name__ == "__main__":
    asyncio.run(main())
