from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.voting.service import VotingService
from app.modules.voting.model import VotingCreate

router = APIRouter(prefix="/voting", tags=["voting"])

voting_service = VotingService()

@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None)
):
    """Get all votings"""
    filters = {}
    if estado:
        filters["estado"] = estado
    return await voting_service.get_all_votings(filters)

@router.get("/{voting_id}")
async def get_voting(
    voting_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Get specific voting"""
    return await voting_service.get_voting(voting_id, user)

@router.post("")
async def create_voting(
    payload: VotingCreate,
    user: dict = Depends(get_current_user)
):
    """Create voting (admin/directiva only)"""
    return await voting_service.create_voting(payload, user)

@router.post("/{voting_id}/vote")
async def vote(
    voting_id: UUID,
    opcion: str = Query(...),
    user: dict = Depends(get_current_user)
):
    """Cast a vote"""
    return await voting_service.vote(voting_id, opcion, user)

@router.patch("/{voting_id}/close")
async def close_voting(
    voting_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Close voting (admin only)"""
    return await voting_service.close_voting(voting_id, user)