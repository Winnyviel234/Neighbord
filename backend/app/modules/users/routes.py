from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from uuid import UUID
from app.core.security import get_current_user, require_permissions
from app.modules.users.service import UserService
from app.modules.users.model import UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()

@router.get("", response_model=List[UserResponse])
async def get_users(
    sector_id: Optional[UUID] = Query(None),
    role_name: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    activo: Optional[bool] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Get users with optional filters"""
    filters = {}
    if sector_id:
        filters["sector_id"] = sector_id
    if role_name:
        filters["role_name"] = role_name
    if estado:
        filters["estado"] = estado
    if activo is not None:
        filters["activo"] = activo
    
    return await user_service.get_users(user, filters)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, user: dict = Depends(get_current_user)):
    """Get specific user"""
    # Users can see themselves, admin/directiva can see anyone
    if str(user_id) != user["id"] and user.get("role_name") not in ["admin", "directiva"]:
        raise HTTPException(403, "No tienes permisos para ver este usuario")
    
    return await user_service.get_user(user_id)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    user: dict = Depends(get_current_user)
):
    """Update user"""
    return await user_service.update_user(user_id, payload, user)

@router.post("/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: UUID,
    user: dict = Depends(require_permissions("manage_users"))
):
    """Approve user registration"""
    return await user_service.approve_user(user_id, user)

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    user: dict = Depends(require_permissions("all"))
):
    """Deactivate user (admin only)"""
    return await user_service.deactivate_user(user_id, user)