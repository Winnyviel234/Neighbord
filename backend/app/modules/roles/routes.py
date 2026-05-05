from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from app.core.security import get_current_user, require_permissions
from app.modules.roles.service import RoleService
from app.modules.roles.model import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])
role_service = RoleService()

@router.get("", response_model=List[RoleResponse])
async def list_roles(user: dict = Depends(get_current_user)):
    return await role_service.get_roles()

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID, user: dict = Depends(get_current_user)):
    return await role_service.get_role(role_id)

@router.post("", response_model=RoleResponse)
async def create_role(payload: RoleCreate, user: dict = Depends(require_permissions("all"))):
    return await role_service.create_role(payload)

@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(role_id: UUID, payload: RoleUpdate, user: dict = Depends(require_permissions("all"))):
    return await role_service.update_role(role_id, payload)

@router.delete("/{role_id}")
async def delete_role(role_id: UUID, user: dict = Depends(require_permissions("all"))):
    return await role_service.delete_role(role_id)
