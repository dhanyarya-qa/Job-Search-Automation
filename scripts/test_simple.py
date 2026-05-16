"""Simple test to verify system is working"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.utils.logging import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger(__name__)

logger.info("Testing system configuration")
logger.info("App name", name=settings.app_name)
logger.info("Database URL", db=settings.database_url)
logger.info("Output dir", output=settings.output_dir)
logger.info("AI Provider", provider=settings.primary_ai_provider)

# Create test output
from app.scraper.output_writer import OutputWriter
writer = OutputWriter()

test_jobs = [
    {
        "title": "QA Automation Engineer",
        "company": "Tech Corp",
        "location": "Jakarta",
        "url": "https://example.com/job1",
        "description": "Looking for QA with Playwright experience",
        "posted_date": "2026-05-16",
        "source": "test"
    },
    {
        "title": "Prompt Engineer",
        "company": "AI Startup",
        "location": "Remote",
        "url": "https://example.com/job2",
        "description": "AI prompt engineering role",
        "posted_date": "2026-05-16",
        "source": "test"
    }
]

writer.write_jobs_json(test_jobs, "test_output")
writer.write_jobs_csv(test_jobs, "test_output")

logger.info("Test complete! Check outputs/ folder")
print("\n✅ System is working!")
print(f"📁 Check: {settings.output_dir}/json/test_output.json")
print(f"📁 Check: {settings.output_dir}/csv/test_output.csv")
