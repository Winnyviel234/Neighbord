from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class NotificationRepository:
    def __init__(self):
        self.notifications_table = table("notifications")
    
    async def get_user_notifications(self, user_id: UUID, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = self.notifications_table.select("*").eq("user_id", str(user_id))
        
        if unread_only:
            query = query.eq("read", False)
        
        result = query.order("created_at", desc=True).execute()
        return result.data or []
    
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
    
    async def mark_multiple_as_read(self, notification_ids: Optional[List[UUID]] = None, user_id: Optional[str] = None) -> bool:
        """Mark multiple notifications as read"""
        query = self.notifications_table
        if notification_ids:
            id_strings = [str(nid) for nid in notification_ids]
            query = query.in_("id", id_strings)
        elif user_id:
            query = query.eq("user_id", str(user_id))
        else:
            return False

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