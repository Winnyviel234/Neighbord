from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table
from app.modules.base import BaseRepository

class ComplaintRepository(BaseRepository):
    def __init__(self):
        self.table = table("solicitudes")
        self.comments_table = table("complaint_comments")
    
    async def get_by_id(self, id: UUID) -> Optional[Dict[str, Any]]:
        """Get complaint by ID with user info"""
        try:
            result = self.table.select("""
                solicitudes.*,
                usuarios.nombre as user_name,
                assigned.nombre as assigned_name
            """).eq("solicitudes.id", str(id)).single().execute()
            return result.data
        except:
            return None
    
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all complaints with optional filters"""
        query = self.table.select("""
            solicitudes.*,
            usuarios.nombre as user_name,
            assigned.nombre as assigned_name
        """)
        
        if filters:
            if filters.get("user_id"):
                query = query.eq("usuario_id", str(filters["user_id"]))
            if filters.get("status"):
                query = query.eq("estado", filters["status"])
            if filters.get("category"):
                query = query.eq("categoria", filters["category"])
            if filters.get("assigned_to"):
                query = query.eq("assigned_to", str(filters["assigned_to"]))
            if filters.get("sector_id"):
                # Filter by user's sector
                query = query.eq("usuarios.sector_id", str(filters["sector_id"]))
        
        result = query.execute()
        return result.data or []
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new complaint"""
        result = self.table.insert(data).execute()
        return result.data[0]
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update complaint"""
        data["updated_at"] = "now()"
        result = self.table.update(data).eq("id", str(id)).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, id: UUID) -> bool:
        """Delete complaint"""
        result = self.table.delete().eq("id", str(id)).execute()
        return len(result.data) > 0
    
    async def add_comment(self, complaint_id: UUID, user_id: UUID, comment: str) -> Dict[str, Any]:
        """Add comment to complaint"""
        data = {
            "complaint_id": str(complaint_id),
            "user_id": str(user_id),
            "comment": comment
        }
        result = self.comments_table.insert(data).execute()
        return result.data[0]
    
    async def get_comments(self, complaint_id: UUID) -> List[Dict[str, Any]]:
        """Get comments for a complaint"""
        result = self.comments_table.select("""
            complaint_comments.*,
            usuarios.nombre as user_name
        """).eq("complaint_id", str(complaint_id)).execute()
        return result.data or []