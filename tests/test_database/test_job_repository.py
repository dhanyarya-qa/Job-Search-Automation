"""Tests for job repository."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.job import Job
from app.database.repositories.job_repository import JobRepository


@pytest.mark.asyncio
async def test_create_job(db_session: AsyncSession) -> None:
    repo = JobRepository(db_session)
    job = await repo.create(
        job_title="QA Automation Engineer",
        company_name="Test Corp",
        location="Jakarta",
        source_platform="linkedin",
        job_url="https://linkedin.com/jobs/test-123",
    )
    assert job.id is not None
    assert job.job_title == "QA Automation Engineer"


@pytest.mark.asyncio
async def test_get_by_url(db_session: AsyncSession) -> None:
    repo = JobRepository(db_session)
    url = "https://jobstreet.com/test-job-dedup"
    await repo.create(
        job_title="Test Job",
        company_name="Dedup Co",
        source_platform="jobstreet",
        job_url=url,
    )
    found = await repo.get_by_url(url)
    assert found is not None
    assert found.job_url == url


@pytest.mark.asyncio
async def test_exists_by_url(db_session: AsyncSession) -> None:
    repo = JobRepository(db_session)
    url = "https://glints.com/test-exists"
    exists_before = await repo.exists_by_url(url)
    assert exists_before is False
    await repo.create(
        job_title="Exists Job",
        company_name="Some Co",
        source_platform="glints",
        job_url=url,
    )
    exists_after = await repo.exists_by_url(url)
    assert exists_after is True


@pytest.mark.asyncio
async def test_search(db_session: AsyncSession) -> None:
    repo = JobRepository(db_session)
    await repo.create(
        job_title="Senior Playwright Automation",
        company_name="Playwright Corp",
        source_platform="linkedin",
        job_url="https://linkedin.com/playwright-job-search",
    )
    results = await repo.search("Playwright", limit=10)
    assert any("Playwright" in j.job_title for j in results)
