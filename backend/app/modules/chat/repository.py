from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class ChatRepository:
    def __init__(self):
        self.rooms_table = table("chat_rooms")
        self.messages_table = table("messages")
    
    async def get_room_by_id(self, room_id: UUID) -> Optional[Dict[str, Any]]:
        """Get chat room by ID"""
        try:
            result = self.rooms_table.select("*").eq("id", str(room_id)).single().execute()
            return result.data
        except:
            return None
    
    async def get_rooms_by_sector(self, sector_id: UUID) -> List[Dict[str, Any]]:
        """Get chat rooms for a sector"""
        result = self.rooms_table.select("*").eq("sector_id", str(sector_id)).execute()
        return result.data or []
    
    async def get_all_rooms(self, user_sector_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get all accessible chat rooms"""
        query = self.rooms_table.select("*")
        if user_sector_id:
            query = query.or_("sector_id.is.null", f"sector_id.eq.{user_sector_id}")
        result = query.execute()
        return result.data or []
    
    async def create_room(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new chat room"""
        result = self.rooms_table.insert(data).execute()
        return result.data[0]
    
    async def delete_room(self, room_id: UUID) -> bool:
        """Delete chat room"""
        result = self.rooms_table.delete().eq("id", str(room_id)).execute()
        return len(result.data) > 0
    
    async def get_messages(self, room_id: UUID, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a room"""
        result = self.messages_table.select("""
            messages.*,
            usuarios.nombre as user_name
        """).eq("room_id", str(room_id)).order("created_at", desc=True).limit(limit).execute()
        return result.data or []
    
    async def create_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new message"""
        result = self.messages_table.insert(data).execute()
        return result.data[0]
    
    async def can_access_room(self, room_id: UUID, user_sector_id: Optional[UUID]) -> bool:
        """Check if user can access a room"""
        room = await self.get_room_by_id(room_id)
        if not room:
            return False
        
        # Public rooms (no sector_id) are accessible to all
        if not room.get("sector_id"):
            return True
        
        # Sector-specific rooms only for users in that sector
        return str(room["sector_id"]) == str(user_sector_id)