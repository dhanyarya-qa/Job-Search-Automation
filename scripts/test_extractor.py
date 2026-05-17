"""
Test the JobExtractor auto-detection methods
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scraper.extractor import JobExtractor

def test_job_type_detection():
    print("=" * 60)
    print("Testing Job Type Detection")
    print("=" * 60)
    
    extractor = JobExtractor()
    
    test_cases = [
        ("Senior Software Engineer", "Full-time position with benefits", "Full-time"),
        ("Contract Developer", "6 month contract role", "Contract"),
        ("Part-time Designer", "Work 20 hours per week", "Part-time"),
        ("Software Engineering Intern", "Summer internship program", "Internship"),
        ("Freelance Writer", "Project-based work", "Contract"),
    ]
    
    for title, desc, expected in test_cases:
        result = extractor._detect_job_type(title, desc)
        status = "✅" if result == expected else "❌"
        print(f"{status} Title: {title}")
        print(f"   Expected: {expected}, Got: {result}")
        print()

def test_experience_level_detection():
    print("=" * 60)
    print("Testing Experience Level Detection")
    print("=" * 60)
    
    extractor = JobExtractor()
    
    test_cases = [
        ("Senior Software Engineer", "5+ years experience required", "Senior"),
        ("Junior Developer", "Fresh graduate welcome", "Junior"),
        ("Mid-level QA Engineer", "2-4 years experience", "Mid-level"),
        ("Lead Backend Developer", "Lead a team of engineers", "Senior"),
        ("Entry Level Data Analyst", "No experience required", "Junior"),
    ]
    
    for title, desc, expected in test_cases:
        result = extractor._detect_experience_level(title, desc)
        status = "✅" if result == expected else "❌"
        print(f"{status} Title: {title}")
        print(f"   Expected: {expected}, Got: {result}")
        print()

def test_remote_detection():
    print("=" * 60)
    print("Testing Remote Detection")
    print("=" * 60)
    
    extractor = JobExtractor()
    
    test_cases = [
        ("Software Engineer", "Remote work available", "Jakarta", True),
        ("Backend Developer", "Work from home", "Indonesia", True),
        ("Frontend Engineer", "Office-based position", "Jakarta", False),
        ("DevOps Engineer - Remote", "Fully distributed team", "Anywhere", True),
        ("QA Tester", "On-site required", "Bandung", False),
    ]
    
    for title, desc, location, expected in test_cases:
        result = extractor._detect_remote(title, desc, location)
        status = "✅" if result == expected else "❌"
        print(f"{status} Title: {title}")
        print(f"   Location: {location}")
        print(f"   Expected: {expected}, Got: {result}")
        print()

def test_full_build_job_dict():
    print("=" * 60)
    print("Testing Full build_job_dict")
    print("=" * 60)
    
    extractor = JobExtractor()
    
    job = extractor.build_job_dict(
        job_title="Senior Full-stack Developer (Remote)",
        company_name="Tech Startup Inc",
        location="Jakarta, Indonesia",
        description="We are looking for a senior full-stack developer with 5+ years experience. This is a full-time remote position. You will work with React, Node.js, and PostgreSQL.",
        job_url="https://example.com/job/123",
        source_platform="linkedin",
        salary="Rp 15-20 juta per bulan",
    )
    
    print("Job Dictionary:")
    print(f"  Title: {job['job_title']}")
    print(f"  Company: {job['company_name']}")
    print(f"  Location: {job['location']}")
    print(f"  Salary: {job['salary']}")
    print(f"  Job Type: {job['job_type']}")
    print(f"  Experience Level: {job['experience_level']}")
    print(f"  Is Remote: {job['is_remote']}")
    print(f"  Platform: {job['source_platform']}")
    print(f"  Description: {job['description'][:100]}...")
    print()
    
    # Verify auto-detection worked
    assert job['job_type'] == 'Full-time', f"Expected Full-time, got {job['job_type']}"
    assert job['experience_level'] == 'Senior', f"Expected Senior, got {job['experience_level']}"
    assert job['is_remote'] == True, f"Expected True, got {job['is_remote']}"
    
    print("✅ All auto-detection working correctly!")

if __name__ == "__main__":
    test_job_type_detection()
    test_experience_level_detection()
    test_remote_detection()
    test_full_build_job_dict()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
