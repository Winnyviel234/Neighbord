from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.users.repository import UserRepository
from app.modules.users.model import UserCreate, UserUpdate, UserResponse
from app.modules.roles.repository import RoleRepository
from app.modules.sectors.repository import SectorRepository
from app.core.supabase import table

class UserService:
    def __init__(self):
        self.repo = UserRepository()
        self.role_repo = RoleRepository()
        self.sector_repo = SectorRepository()
    
    async def get_user(self, user_id: UUID) -> UserResponse:
        """Get user by ID"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        return UserResponse(**user)
    
    async def get_users(self, current_user: Dict[str, Any], filters: Dict[str, Any] = None) -> List[UserResponse]:
        """Get users with permission check"""
        # Only admin and directiva can see all users
        if current_user.get("role_name") not in ["admin", "directiva"]:
            # Regular users can only see themselves
            user = await self.repo.get_by_id(current_user["id"])
            return [UserResponse(**user)] if user else []
        
        users = await self.repo.get_all(filters)
        return [UserResponse(**user) for user in users]
    
    async def update_user(self, user_id: UUID, data: UserUpdate, current_user: Dict[str, Any]) -> UserResponse:
        """Update user with permission check"""
        # Users can update themselves, admin/directiva can update anyone
        if str(user_id) != current_user["id"] and current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "No tienes permisos para actualizar este usuario")
        
        # Only admin can change roles and status
        if data.estado and current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede cambiar el estado de usuarios")

        if (data.role_id or data.sector_id) and current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede cambiar rol o sector de un usuario")

        if data.role_id:
            role = await self.role_repo.get_by_id(data.role_id)
            if not role:
                raise HTTPException(404, "Rol no encontrado")

        if data.sector_id:
            sector = await self.sector_repo.get_by_id(data.sector_id)
            if not sector:
                raise HTTPException(404, "Sector no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        user = await self.repo.update(user_id, update_data)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")

        return UserResponse(**user)
    
    async def approve_user(self, user_id: UUID, current_user: Dict[str, Any]) -> UserResponse:
        """Approve user registration (admin/directiva only)"""
        if current_user.get("role_name") not in ["admin", "directiva"]:
            raise HTTPException(403, "No tienes permisos para aprobar usuarios")
        
        user = await self.repo.update(user_id, {"estado": "aprobado"})
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        return UserResponse(**user)
    
    async def deactivate_user(self, user_id: UUID, current_user: Dict[str, Any]) -> UserResponse:
        """Deactivate user (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede desactivar usuarios")
        
        user = await self.repo.update(user_id, {"activo": False})
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        return UserResponse(**user)