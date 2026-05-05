from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.meetings.service import MeetingService
from app.modules.meetings.model import MeetingCreate, MeetingUpdate

router = APIRouter(prefix="/meetings", tags=["meetings"])

meeting_service = MeetingService()

@router.get("")
async def get_meetings(
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None)
):
    """Get all meetings"""
    filters = {}
    if tipo:
        filters["tipo"] = tipo
    if estado:
        filters["estado"] = estado
    return await meeting_service.get_all_meetings(filters)

@router.get("/{meeting_id}")
async def get_meeting(meeting_id: UUID):
    """Get specific meeting"""
    return await meeting_service.get_meeting(meeting_id)

@router.post("")
async def create_meeting(
    payload: MeetingCreate,
    user: dict = Depends(get_current_user)
):
    """Create meeting (admin/directiva only)"""
    return await meeting_service.create_meeting(payload, user)

@router.patch("/{meeting_id}")
async def update_meeting(
    meeting_id: UUID,
    payload: MeetingUpdate,
    user: dict = Depends(get_current_user)
):
    """Update meeting (admin/directiva only)"""
    return await meeting_service.update_meeting(meeting_id, payload, user)

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Delete meeting (admin only)"""
    return await meeting_service.delete_meeting(meeting_id, user)

@router.post("/{meeting_id}/attend")
async def register_attendance(
    meeting_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Register attendance"""
    return await meeting_service.register_attendance(meeting_id, user)

@router.get("/{meeting_id}/attendances")
async def get_attendances(meeting_id: UUID):
    """Get attendances for a meeting"""
    return await meeting_service.get_attendances(meeting_id)