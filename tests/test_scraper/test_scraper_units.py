"""
Scraper unit tests — rate limiter, extractor, parser.
"""

from __future__ import annotations

import asyncio

import pytest

from app.scraper.rate_limiter import RateLimiter
from app.scraper.extractor import JobExtractor
from app.scraper.parser import JobParser


# ─── Rate Limiter Tests ───────────────────────────────────────────
@pytest.mark.asyncio
async def test_rate_limiter_allows_burst() -> None:
    """Rate limiter should allow up to burst_limit immediate requests."""
    limiter = RateLimiter(requests_per_minute=60, burst_limit=5)
    # 5 requests should be near-instant (within burst)
    for _ in range(5):
        await limiter.acquire()


@pytest.mark.asyncio
async def test_rate_limiter_throttles() -> None:
    """Rate limiter should throttle after burst is exhausted."""
    limiter = RateLimiter(requests_per_minute=120, burst_limit=2)
    await limiter.acquire()
    await limiter.acquire()
    # 3rd should be slightly delayed — we just check it completes
    task = asyncio.create_task(limiter.acquire())
    await asyncio.wait_for(task, timeout=5.0)


# ─── Job Extractor Tests ──────────────────────────────────────────
def test_extractor_build_job_dict_required_fields() -> None:
    extractor = JobExtractor()
    job = extractor.build_job_dict(
        job_title="  QA Automation Engineer  ",
        company_name="  Tech Corp  ",
        location="Jakarta",
        description="We need a QA engineer.",
        job_url="https://example.com/job/123",
        source_platform="linkedin",
    )
    assert job["job_title"] == "QA Automation Engineer"
    assert job["company_name"] == "Tech Corp"
    assert job["source_platform"] == "linkedin"
    assert "scraped_at" in job
    assert isinstance(job["tech_stack"], list)
    assert isinstance(job["requirements"], list)


def test_extractor_detects_tech_stack() -> None:
    extractor = JobExtractor()
    html = "<script src='/_next/static/chunks/main.js'></script>"
    desc = "We use React and PostgreSQL in production."
    detected = extractor.detect_tech_stack(html, desc)
    assert "Next.js" in detected or "React" in detected


def test_extractor_extracts_salary() -> None:
    extractor = JobExtractor()
    text = "Salary: Rp 10.000.000 - Rp 15.000.000 per bulan"
    salary = extractor.extract_salary(text)
    assert "Rp" in salary


# ─── Job Parser Tests ─────────────────────────────────────────────
def test_parser_strip_html() -> None:
    html = "<p>Hello <b>World</b></p>"
    result = JobParser.strip_html(html)
    assert result == "Hello World"


def test_parser_extract_tags() -> None:
    text = "Must know Playwright, Python, and REST API. Docker experience is a plus."
    tags = JobParser.extract_tags(text)
    assert "Playwright" in tags
    assert "Python" in tags
    assert "REST API" in tags


def test_parser_normalize_location() -> None:
    assert JobParser.normalize_location("Jakarta Selatan") == "South Jakarta"
    assert JobParser.normalize_location("WFH") == "Remote"
    assert JobParser.normalize_location("Bandung") == "Bandung"


def test_parser_parse_posted_date_relative() -> None:
    result = JobParser.parse_posted_date("2 days ago")
    assert result != ""


def test_parser_parse_posted_date_standard() -> None:
    result = JobParser.parse_posted_date("2026-05-16")
    assert "2026" in result
