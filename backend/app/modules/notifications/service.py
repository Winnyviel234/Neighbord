from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.model import NotificationCreate, NotificationResponse, NotificationMarkRead

class NotificationService:
    def __init__(self):
        self.repo = NotificationRepository()
    
    async def get_user_notifications(self, user_id: UUID, unread_only: bool = False) -> List[NotificationResponse]:
        """Get user notifications"""
        notifications = await self.repo.get_user_notifications(user_id, unread_only)
        return [NotificationResponse(**n) for n in notifications]
    
    async def get_notification(self, notification_id: UUID) -> NotificationResponse:
        """Get specific notification"""
        notification = await self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(404, "Notificación no encontrada")
        return NotificationResponse(**notification)
    
    async def create_notification(self, data: NotificationCreate, user_id: UUID) -> NotificationResponse:
        """Create notification (internal use)"""
        notification_data = {
            "user_id": str(user_id),
            "titulo": data.titulo,
            "mensaje": data.contenido,
            "tipo": data.tipo,
            "referencia_id": str(data.referencia_id) if data.referencia_id else None,
            "referencia_tipo": data.referencia_tipo,
            "read": False
        }
        
        notification = await self.repo.create(notification_data)
        return NotificationResponse(**notification)
    
    async def mark_as_read(self, notification_id: UUID, current_user: Dict[str, Any]) -> NotificationResponse:
        """Mark notification as read"""
        notification = await self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(404, "Notificación no encontrada")
        
        # Verify ownership
        if str(notification["user_id"]) != current_user["id"]:
            raise HTTPException(403, "No puedes marcar la notificación de otro usuario")
        
        notification = await self.repo.mark_as_read(notification_id)
        return NotificationResponse(**notification)
    
    async def mark_multiple_as_read(self, data: NotificationMarkRead, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Mark multiple notifications as read"""
        if not data.ids:
            await self.repo.mark_multiple_as_read(user_id=current_user["id"])
            return {"message": "Notificaciones marcadas como leídas"}

        # Verify all notifications belong to user
        for nid in data.ids:
            notification = await self.repo.get_by_id(nid)
            if not notification or str(notification["user_id"]) != current_user["id"]:
                raise HTTPException(403, "Una o más notificaciones no pertenecen a ti")

        await self.repo.mark_multiple_as_read(data.ids)
        return {"message": "Notificaciones marcadas como leídas"}
    
    async def delete_notification(self, notification_id: UUID, current_user: Dict[str, Any]) -> Dict[str, str]:
        """Delete notification"""
        notification = await self.repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(404, "Notificación no encontrada")
        
        # Verify ownership
        if str(notification["user_id"]) != current_user["id"]:
            raise HTTPException(403, "No puedes eliminar la notificación de otro usuario")
        
        success = await self.repo.delete(notification_id)
        if not success:
            raise HTTPException(404, "Notificación no encontrada")
        
        return {"message": "Notificación eliminada"}
    
    async def get_unread_count(self, user_id: UUID) -> Dict[str, int]:
        """Get count of unread notifications"""
        count = await self.repo.get_unread_count(user_id)
        return {"unread_count": count}