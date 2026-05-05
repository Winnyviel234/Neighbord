from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table
from app.modules.base import BaseRepository

class SectorRepository(BaseRepository):
    def __init__(self):
        self.table = table("sectors")
    
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get sector by ID"""
        try:
            result = self.table.select("*").eq("id", str(id)).single().execute()
            return result.data
        except:
            return None
    
    async def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get sector by name"""
        try:
            result = self.table.select("*").eq("name", name).single().execute()
            return result.data
        except:
            return None
    
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all sectors"""
        query = self.table.select("*")
        result = query.execute()
        return result.data or []
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new sector"""
        result = self.table.insert(data).execute()
        return result.data[0]
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update sector"""
        result = self.table.update(data).eq("id", str(id)).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, id: UUID) -> bool:
        """Delete sector (only if no users assigned)"""
        # Check if sector has users
        users = table("usuarios").select("id").eq("sector_id", str(id)).execute()
        if users.data:
            return False  # Cannot delete sector with users
        
        result = self.table.delete().eq("id", str(id)).execute()
        return len(result.data) > 0