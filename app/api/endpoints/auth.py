"""
Auth Endpoints — Login and OTP verification.
"""

from __future__ import annotations

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.auth.otp_handler import (
    generate_otp,
    get_otp_expiry,
    hash_otp,
    is_otp_expired,
    verify_otp,
)
from app.config import settings
from app.database.models.otp_session import OTPSession
from app.database.session import get_async_session

logger = structlog.get_logger(__name__)
router = APIRouter()

# Simple single-user auth using candidate name from settings
VALID_USER = settings.candidate_name


class LoginRequest(BaseModel):
    username: str


class OTPVerifyRequest(BaseModel):
    username: str
    otp_code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=dict)
async def request_otp(
    body: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Request OTP for login. In production, OTP is sent via Telegram/Email."""
    try:
        if body.username.strip().lower() != VALID_USER.lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")

        otp = generate_otp()
        otp_record = OTPSession(
            user_identifier=body.username,
            otp_hash=hash_otp(otp),
            purpose="login",
            expires_at=get_otp_expiry(),
        )
        session.add(otp_record)
        await session.commit()

        # In dev mode, return OTP directly. In production, send via Telegram.
        if settings.debug:
            logger.warning("DEBUG MODE: OTP returned in response", otp=otp)
            return {"message": "OTP generated (debug mode)", "otp": otp}

        # TODO: send OTP via Telegram or Email in production
        logger.info("OTP generated for user", user=body.username)
        return {"message": "OTP sent to registered contact"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in request_otp", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp_endpoint(
    body: OTPVerifyRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Verify OTP and issue JWT tokens."""
    from sqlalchemy import select  # noqa: PLC0415

    result = await session.execute(
        select(OTPSession)
        .where(
            OTPSession.user_identifier == body.username,
            OTPSession.is_used == False,  # noqa: E712
            OTPSession.purpose == "login",
        )
        .order_by(OTPSession.created_at.desc())
        .limit(1)
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active OTP session")

    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP expired")

    if not verify_otp(body.otp_code, otp_record.otp_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    otp_record.is_used = True
    await session.commit()
    
    data = {"sub": body.username}
    return TokenResponse(
        access_token=create_access_token(data),
        refresh_token=create_refresh_token(data),
    )
