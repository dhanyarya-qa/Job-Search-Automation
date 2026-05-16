"""
Health Endpoint — System health check.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()


@router.get("/", response_class=ORJSONResponse)
async def health() -> dict:
    return {"status": "ok", "service": "Ultimate Job Hunting ATS"}
