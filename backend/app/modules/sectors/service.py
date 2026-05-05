from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.sectors.repository import SectorRepository
from app.modules.sectors.model import SectorCreate, SectorUpdate, SectorResponse
from app.core.supabase import table

class SectorService:
    def __init__(self):
        self.repo = SectorRepository()
    
    async def get_sector(self, sector_id: UUID) -> SectorResponse:
        """Get sector by ID"""
        sector = await self.repo.get_by_id(sector_id)
        if not sector:
            raise HTTPException(404, "Sector no encontrado")
        
        return SectorResponse(**sector)
    
    async def get_sectors(self) -> List[SectorResponse]:
        """Get all sectors"""
        sectors = await self.repo.get_all()
        return [SectorResponse(**sector) for sector in sectors]
    
    async def create_sector(self, data: SectorCreate, current_user: Dict[str, Any]) -> SectorResponse:
        """Create new sector (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede crear sectores")
        
        # Check if name exists
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(409, "Ya existe un sector con ese nombre")
        
        sector_data = data.model_dump()
        sector = await self.repo.create(sector_data)
        
        return SectorResponse(**sector)
    
    async def update_sector(self, sector_id: UUID, data: SectorUpdate, current_user: Dict[str, Any]) -> SectorResponse:
        """Update sector (admin only)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede actualizar sectores")
        
        # Check if new name conflicts
        if data.name:
            existing = await self.repo.get_by_name(data.name)
            if existing and str(existing["id"]) != str(sector_id):
                raise HTTPException(409, "Ya existe un sector con ese nombre")
        
        update_data = data.model_dump(exclude_unset=True)
        sector = await self.repo.update(sector_id, update_data)
        if not sector:
            raise HTTPException(404, "Sector no encontrado")
        
        return SectorResponse(**sector)
    
    async def delete_sector(self, sector_id: UUID, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Delete sector (admin only, only if empty)"""
        if current_user.get("role_name") != "admin":
            raise HTTPException(403, "Solo el administrador puede eliminar sectores")
        
        success = await self.repo.delete(sector_id)
        if not success:
            raise HTTPException(409, "No se puede eliminar el sector porque tiene usuarios asignados")
        
        return {"message": "Sector eliminado exitosamente"}
    
    async def get_sector_users(self, sector_id: UUID, current_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get users in a sector"""
        # Only admin/directiva can see users from other sectors
        if current_user.get("role_name") not in ["admin", "directiva"] and str(current_user.get("sector_id")) != str(sector_id):
            raise HTTPException(403, "No tienes permisos para ver usuarios de este sector")
        
        # Verify sector exists
        sector = await self.repo.get_by_id(sector_id)
        if not sector:
            raise HTTPException(404, "Sector no encontrado")
        
        # Get users
        users = table("usuarios").select("""
            usuarios.*,
            roles.name as role_name
        """).eq("sector_id", str(sector_id)).execute()
        
        return users.data or []