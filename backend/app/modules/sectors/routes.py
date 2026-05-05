from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.core.security import get_current_user, require_permissions
from app.modules.sectors.service import SectorService
from app.modules.sectors.model import SectorCreate, SectorUpdate, SectorResponse

router = APIRouter(prefix="/sectors", tags=["sectors"])

sector_service = SectorService()

@router.get("", response_model=List[SectorResponse])
async def get_sectors():
    """Get all sectors"""
    return await sector_service.get_sectors()

@router.get("/{sector_id}", response_model=SectorResponse)
async def get_sector(sector_id: UUID):
    """Get specific sector"""
    return await sector_service.get_sector(sector_id)

@router.post("", response_model=SectorResponse)
async def create_sector(
    payload: SectorCreate,
    user: dict = Depends(require_permissions("all"))
):
    """Create new sector (admin only)"""
    return await sector_service.create_sector(payload, user)

@router.patch("/{sector_id}", response_model=SectorResponse)
async def update_sector(
    sector_id: UUID,
    payload: SectorUpdate,
    user: dict = Depends(require_permissions("all"))
):
    """Update sector (admin only)"""
    return await sector_service.update_sector(sector_id, payload, user)

@router.delete("/{sector_id}")
async def delete_sector(
    sector_id: UUID,
    user: dict = Depends(require_permissions("all"))
):
    """Delete sector (admin only)"""
    return await sector_service.delete_sector(sector_id, user)

@router.get("/{sector_id}/users")
async def get_sector_users(
    sector_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Get users in a sector"""
    return await sector_service.get_sector_users(sector_id, user)