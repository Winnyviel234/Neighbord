from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table
from app.modules.base import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        self.table = table("usuarios")
    
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID with role and sector info"""
        try:
            result = self.table.select("""
                usuarios.*,
                roles.name as role_name,
                roles.permissions as role_permissions,
                sectors.name as sector_name
            """).eq("usuarios.id", str(id)).single().execute()
            return result.data
        except:
            return None
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.table.select("""
                usuarios.*,
                roles.name as role_name,
                sectors.name as sector_name
            """).eq("email", email).single().execute()
            return result.data
        except:
            return None
    
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all users with optional filters"""
        query = self.table.select("""
            usuarios.*,
            roles.name as role_name,
            sectors.name as sector_name
        """)
        
        if filters:
            if filters.get("sector_id"):
                query = query.eq("sector_id", str(filters["sector_id"]))
            if filters.get("role_name"):
                query = query.eq("roles.name", filters["role_name"])
            if filters.get("estado"):
                query = query.eq("estado", filters["estado"])
            if filters.get("activo") is not None:
                query = query.eq("activo", filters["activo"])
        
        result = query.execute()
        return result.data or []
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        result = self.table.insert(data).execute()
        return result.data[0]
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        result = self.table.update(data).eq("id", str(id)).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, id: UUID) -> bool:
        """Soft delete user (deactivate)"""
        result = self.table.update({"activo": False}).eq("id", str(id)).execute()
        return len(result.data) > 0