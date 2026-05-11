from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class NotificationRepository:
    def __init__(self):
        self.notifications_table = table("notifications")
        self.preferences_table = table("preferencias_notificaciones")
    
    async def get_user_notifications(self, user_id: UUID, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = self.notifications_table.select("*").eq("user_id", str(user_id))
        
        if unread_only:
            query = query.eq("read", False)
        
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    async def get_user_preferences(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get or create notification preferences for a user"""
        result = self.preferences_table.select("*").eq("usuario_id", str(user_id)).execute()
        if result.data:
            return result.data[0]
        return None

    async def save_user_preferences(self, user_id: UUID, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update notification preferences for a user"""
        data = {"usuario_id": str(user_id), **prefs}
        result = self.preferences_table.upsert(data, on_conflict="usuario_id").execute()
        return result.data[0] if result.data else data
    
    async def get_by_id(self, notification_id: UUID) -> Optional[Dict[str, Any]]:
        """Get notification by ID"""
        result = self.notifications_table.select("*").eq("id", str(notification_id)).single().execute()
        return result.data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification"""
        result = self.notifications_table.insert(data).execute()
        return result.data[0]
    
    async def mark_as_read(self, notification_id: UUID) -> Optional[Dict[str, Any]]:
        """Mark notification as read"""
        result = self.notifications_table.update({"read": True}).eq("id", str(notification_id)).execute()
        return result.data[0] if result.data else None
    
    async def mark_multiple_as_read(self, notification_ids: List[UUID]) -> bool:
        """Mark multiple notifications as read"""
        id_strings = [str(nid) for nid in notification_ids]
        # Using in_ filter for multiple IDs
        query = self.notifications_table
        for nid in id_strings:
            query = query.or_(f"id.eq.{nid}")
        
        result = query.update({"read": True}).execute()
        return len(result.data) > 0
    
    async def delete(self, notification_id: UUID) -> bool:
        """Delete notification"""
        result = self.notifications_table.delete().eq("id", str(notification_id)).execute()
        return len(result.data) > 0
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications"""
        result = self.notifications_table.select("id", count="exact").eq("user_id", str(user_id)).eq("read", False).execute()
        return result.count or 0