"""
Application Tracking API Endpoints
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.application_tracking import ApplicationStatus, ApplicationTracking
from app.database.models.job import Job
from app.database.session import get_async_session
from app.notifications.telegram_notifier import TelegramNotifier

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/tracking", tags=["Application Tracking"])


# ─── Schemas ──────────────────────────────────────────────────────
class ApplicationTrackingCreate(BaseModel):
    job_id: int
    status: str = ApplicationStatus.SAVED.value
    notes: str | None = None


class ApplicationTrackingUpdate(BaseModel):
    status: str | None = None
    application_method: str | None = None
    cover_letter_sent: bool | None = None
    interview_date: datetime | None = None
    interview_type: str | None = None
    interview_notes: str | None = None
    offer_amount: str | None = None
    offer_deadline: datetime | None = None
    rejection_reason: str | None = None
    notes: str | None = None


class ApplicationTrackingResponse(BaseModel):
    id: int
    job_id: int
    status: str
    applied_at: datetime | None
    interview_date: datetime | None
    offer_received_at: datetime | None
    rejected_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Endpoints ────────────────────────────────────────────────────
@router.post("/", response_model=ApplicationTrackingResponse)
async def create_tracking(
    data: ApplicationTrackingCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Create new application tracking"""
    
    # Verify job exists
    result = await session.execute(select(Job).where(Job.id == data.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    tracking = ApplicationTracking(
        job_id=data.job_id,
        status=data.status,
        notes=data.notes,
    )
    
    session.add(tracking)
    await session.commit()
    await session.refresh(tracking)
    
    logger.info("Application tracking created", tracking_id=tracking.id, job_id=data.job_id)
    return tracking


@router.get("/", response_model=list[ApplicationTrackingResponse])
async def list_tracking(
    status: str | None = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """List all application tracking records"""
    
    query = select(ApplicationTracking).order_by(ApplicationTracking.updated_at.desc())
    
    if status:
        query = query.where(ApplicationTracking.status == status)
    
    query = query.limit(limit)
    
    result = await session.execute(query)
    trackings = result.scalars().all()
    
    return trackings


@router.get("/{tracking_id}", response_model=ApplicationTrackingResponse)
async def get_tracking(
    tracking_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get specific application tracking"""
    
    result = await session.execute(
        select(ApplicationTracking).where(ApplicationTracking.id == tracking_id)
    )
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    
    return tracking


@router.patch("/{tracking_id}", response_model=ApplicationTrackingResponse)
async def update_tracking(
    tracking_id: int,
    data: ApplicationTrackingUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Update application tracking status"""
    
    result = await session.execute(
        select(ApplicationTracking).where(ApplicationTracking.id == tracking_id)
    )
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(tracking, field, value)
    
    # Update status-specific timestamps
    if data.status:
        tracking.status_updated_at = datetime.now(timezone.utc)
        
        if data.status == ApplicationStatus.APPLIED.value and not tracking.applied_at:
            tracking.applied_at = datetime.now(timezone.utc)
        elif data.status == ApplicationStatus.OFFER.value and not tracking.offer_received_at:
            tracking.offer_received_at = datetime.now(timezone.utc)
        elif data.status == ApplicationStatus.REJECTED.value and not tracking.rejected_at:
            tracking.rejected_at = datetime.now(timezone.utc)
    
    await session.commit()
    await session.refresh(tracking)
    
    logger.info("Application tracking updated", tracking_id=tracking_id, status=tracking.status)
    
    # Send Telegram notification for important status changes
    if data.status in [ApplicationStatus.INTERVIEW_SCHEDULED.value, ApplicationStatus.OFFER.value, ApplicationStatus.REJECTED.value]:
        try:
            notifier = TelegramNotifier()
            await _send_status_notification(notifier, tracking, session)
        except Exception as e:
            logger.error("Failed to send Telegram notification", error=str(e))
    
    return tracking


@router.delete("/{tracking_id}")
async def delete_tracking(
    tracking_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Delete application tracking"""
    
    result = await session.execute(
        select(ApplicationTracking).where(ApplicationTracking.id == tracking_id)
    )
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    
    await session.delete(tracking)
    await session.commit()
    
    logger.info("Application tracking deleted", tracking_id=tracking_id)
    return {"message": "Tracking deleted successfully"}


@router.get("/stats/summary")
async def get_tracking_stats(
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get application tracking statistics"""
    
    result = await session.execute(select(ApplicationTracking))
    all_trackings = result.scalars().all()
    
    stats = {
        "total": len(all_trackings),
        "by_status": {},
        "interviews_scheduled": 0,
        "offers_received": 0,
        "applications_sent": 0,
    }
    
    for tracking in all_trackings:
        # Count by status
        status = tracking.status
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Count specific milestones
        if tracking.applied_at:
            stats["applications_sent"] += 1
        if tracking.interview_date:
            stats["interviews_scheduled"] += 1
        if tracking.offer_received_at:
            stats["offers_received"] += 1
    
    return stats


# ─── Helper Functions ─────────────────────────────────────────────
async def _send_status_notification(
    notifier: TelegramNotifier,
    tracking: ApplicationTracking,
    session: AsyncSession,
) -> None:
    """Send Telegram notification for status updates"""
    
    # Get job details
    result = await session.execute(select(Job).where(Job.id == tracking.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        return
    
    status = tracking.status
    
    if status == ApplicationStatus.INTERVIEW_SCHEDULED.value:
        text = (
            f"📅 <b>Interview Scheduled!</b>\n\n"
            f"📋 {job.job_title}\n"
            f"🏢 {job.company_name}\n"
        )
        if tracking.interview_date:
            text += f"📆 Date: {tracking.interview_date.strftime('%d %b %Y, %H:%M')}\n"
        if tracking.interview_type:
            text += f"📞 Type: {tracking.interview_type.title()}\n"
        
    elif status == ApplicationStatus.OFFER.value:
        text = (
            f"🎉 <b>Offer Received!</b>\n\n"
            f"📋 {job.job_title}\n"
            f"🏢 {job.company_name}\n"
        )
        if tracking.offer_amount:
            text += f"💰 Offer: {tracking.offer_amount}\n"
        if tracking.offer_deadline:
            text += f"⏰ Deadline: {tracking.offer_deadline.strftime('%d %b %Y')}\n"
        
    elif status == ApplicationStatus.REJECTED.value:
        text = (
            f"❌ <b>Application Rejected</b>\n\n"
            f"📋 {job.job_title}\n"
            f"🏢 {job.company_name}\n"
        )
        if tracking.rejection_reason:
            text += f"\n📝 Reason: {tracking.rejection_reason}\n"
    
    else:
        return
    
    await notifier.send_message(text)
