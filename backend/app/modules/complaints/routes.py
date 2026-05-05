from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.complaints.service import ComplaintService
from app.modules.complaints.model import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintCommentCreate

router = APIRouter(prefix="/complaints", tags=["complaints"])

complaint_service = ComplaintService()

@router.get("", response_model=List[ComplaintResponse])
async def get_complaints(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Get complaints with optional filters"""
    filters = {}
    if status:
        filters["status"] = status
    if category:
        filters["category"] = category
    if priority:
        filters["priority"] = priority
    
    return await complaint_service.get_complaints(user, filters)

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Get specific complaint"""
    return await complaint_service.get_complaint(complaint_id, user)

@router.post("", response_model=ComplaintResponse)
async def create_complaint(
    payload: ComplaintCreate,
    user: dict = Depends(get_current_user)
):
    """Create new complaint"""
    return await complaint_service.create_complaint(payload, user)

@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: UUID,
    payload: ComplaintUpdate,
    user: dict = Depends(get_current_user)
):
    """Update complaint"""
    return await complaint_service.update_complaint(complaint_id, payload, user)

@router.delete("/{complaint_id}")
async def delete_complaint(
    complaint_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Delete complaint (admin only)"""
    return await complaint_service.delete_complaint(complaint_id, user)

@router.post("/{complaint_id}/comments")
async def add_comment(
    complaint_id: UUID,
    payload: ComplaintCommentCreate,
    user: dict = Depends(get_current_user)
):
    """Add comment to complaint"""
    return await complaint_service.add_comment(complaint_id, payload, user)

@router.get("/{complaint_id}/comments")
async def get_comments(
    complaint_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Get comments for a complaint"""
    return await complaint_service.get_comments(complaint_id, user)