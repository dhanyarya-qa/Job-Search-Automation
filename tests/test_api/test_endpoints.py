"""API endpoint tests."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(api_client: AsyncClient) -> None:
    resp = await api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_jobs_requires_auth(api_client: AsyncClient) -> None:
    resp = await api_client.get("/api/v1/jobs/")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_login_invalid_user(api_client: AsyncClient) -> None:
    resp = await api_client.post(
        "/api/v1/auth/login",
        json={"username": "unknown_user_xyz"},
    )
    assert resp.status_code == 401
