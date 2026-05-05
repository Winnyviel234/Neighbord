from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class MeetingRepository:
    def __init__(self):
        self.meetings_table = table("reuniones")
        self.attendance_table = table("asistencias")
    
    async def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all meetings"""
        query = self.meetings_table.select("""
            reuniones.*,
            usuarios.nombre as creado_por_nombre,
            COUNT(asistencias.id) as asistentes
        """)
        
        if filters:
            if filters.get("tipo"):
                query = query.eq("tipo", filters["tipo"])
            if filters.get("estado"):
                query = query.eq("estado", filters["estado"])
        
        result = query.execute()
        return result.data or []
    
    async def get_by_id(self, meeting_id: UUID) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        result = self.meetings_table.select("""
            reuniones.*,
            usuarios.nombre as creado_por_nombre
        """).eq("id", str(meeting_id)).single().execute()
        return result.data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create meeting"""
        result = self.meetings_table.insert(data).execute()
        return result.data[0]
    
    async def update(self, meeting_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update meeting"""
        result = self.meetings_table.update(data).eq("id", str(meeting_id)).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, meeting_id: UUID) -> bool:
        """Delete meeting"""
        result = self.meetings_table.delete().eq("id", str(meeting_id)).execute()
        return len(result.data) > 0
    
    async def add_attendance(self, meeting_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Record attendance"""
        data = {
            "reunion_id": str(meeting_id),
            "usuario_id": str(user_id)
        }
        result = self.attendance_table.insert(data).execute()
        return result.data[0]
    
    async def get_attendances(self, meeting_id: UUID) -> List[Dict[str, Any]]:
        """Get attendances for a meeting"""
        result = self.attendance_table.select("""
            asistencias.*,
            usuarios.nombre as usuario_nombre
        """).eq("reunion_id", str(meeting_id)).execute()
        return result.data or []
    
    async def is_attended(self, meeting_id: UUID, user_id: UUID) -> bool:
        """Check if user attended"""
        result = self.attendance_table.select("id").eq("reunion_id", str(meeting_id)).eq("usuario_id", str(user_id)).execute()
        return len(result.data) > 0