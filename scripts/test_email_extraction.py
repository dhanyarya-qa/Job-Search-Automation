"""Test email and apply link extraction"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scraper.extractor import JobExtractor
from app.scraper.output_writer import OutputWriter

# Test data dengan email dan apply link
test_html = """
<html>
<body>
    <h1>QA Automation Engineer</h1>
    <p>Contact us at: recruitment@techcorp.com</p>
    <p>Or email: hr@techcorp.com for more info</p>
    <a href="/apply/12345" class="apply-button">Apply Now</a>
    <a href="https://careers.techcorp.com/apply">Quick Apply</a>
</body>
</html>
"""

test_description = """
We are looking for a QA Automation Engineer with Playwright experience.

Requirements:
- 3+ years experience in QA
- Playwright, Selenium, or Cypress
- Python or JavaScript

Salary: Rp 10-15 juta per bulan

To apply, send your CV to jobs@techcorp.com
"""

extractor = JobExtractor()

# Test extract email
email = extractor.extract_email(test_description)
print(f"✅ Extracted email: {email}")

# Test extract apply link
apply_link = extractor.extract_apply_link(test_html, "https://techcorp.com/jobs/qa-engineer")
print(f"✅ Extracted apply link: {apply_link}")

# Test build_job_dict dengan auto-extraction
job_dict = extractor.build_job_dict(
    job_title="QA Automation Engineer",
    company_name="Tech Corp",
    location="Jakarta",
    description=test_description,
    job_url="https://techcorp.com/jobs/qa-engineer",
    source_platform="test",
    html_content=test_html
)

print(f"\n📋 Job Dictionary:")
print(f"  Title: {job_dict['job_title']}")
print(f"  Company: {job_dict['company_name']}")
print(f"  Apply Email: {job_dict['apply_email']}")
print(f"  Apply Link: {job_dict['apply_link']}")
print(f"  Salary: {job_dict['salary']}")

# Save to file
writer = OutputWriter()
writer.write_jobs_json([job_dict], "test_with_email")
writer.write_jobs_csv([job_dict], "test_with_email")

print(f"\n✅ Test complete! Files saved to outputs/")
print(f"📁 JSON: outputs/json/test_with_email_*.json")
print(f"📁 CSV: outputs/csv/test_with_email_*.csv")
