from typing import Optional, Dict, Any
from uuid import UUID
from httpx import HTTPStatusError
from app.core.supabase import table
from app.modules.base import BaseRepository

class AuthRepository(BaseRepository):
    def __init__(self):
        self.table = table("usuarios")
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email with role information"""
        try:
            result = self.table.select("""
                usuarios.*,
                roles.name as role_name,
                roles.permissions as role_permissions,
                sectors.name as sector_name
            """).eq("email", email).single().execute()
            return result.data
        except HTTPStatusError:
            return None
    
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID with role and sector"""
        try:
            result = self.table.select("""
                usuarios.*,
                roles.name as role_name,
                roles.permissions as role_permissions,
                sectors.name as sector_name
            """).eq("id", str(id)).single().execute()
            return result.data
        except HTTPStatusError:
            return None
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        # Get default role (vecino)
        try:
            role_result = table("roles").select("id").eq("name", "vecino").single().execute()
        except HTTPStatusError as exc:
            raise RuntimeError(
                "No se puede obtener el rol predeterminado 'vecino'. "
                "Verifica que la tabla roles exista y que la configuración de Supabase sea correcta."
            ) from exc

        if not role_result.data:
            raise RuntimeError("No se encontró el rol predeterminado 'vecino' en la tabla roles.")

        data["role_id"] = role_result.data["id"]
        
        # Set default sector if not provided
        if not data.get("sector_id"):
            sector_result = table("sectors").select("id").limit(1).execute()
            if sector_result.data:
                data["sector_id"] = sector_result.data[0]["id"]
            else:
                raise RuntimeError("No se encontró ningún sector predeterminado en la tabla sectors.")
        
        result = self.table.insert(data).execute()
        if not result.data:
            raise RuntimeError("No se pudo crear el usuario en Supabase.")
        return result.data[0]
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        result = self.table.update(data).eq("id", str(id)).execute()
        return result.data[0] if result.data else None
    
    async def get_all(self, filters: Dict[str, Any] = None) -> list:
        """Not implemented for auth"""
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        """Not implemented for auth"""
        raise NotImplementedError