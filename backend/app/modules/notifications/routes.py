from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.notifications.service import NotificationService
from app.modules.notifications.model import NotificationMarkRead

router = APIRouter(prefix="/notifications", tags=["notifications"])

notification_service = NotificationService()

@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
    user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    return await notification_service.get_user_notifications(user["id"], unread_only)

@router.get("/unread/count")
async def get_unread_count(
    user: dict = Depends(get_current_user)
):
    """Get unread notifications count"""
    return await notification_service.get_unread_count(user["id"])

@router.get("/{notification_id}")
async def get_notification(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Get specific notification"""
    notification = await notification_service.get_notification(notification_id)
    # Verify ownership
    if str(notification.user_id) != user["id"] and user.get("role_name") != "admin":
        from fastapi import HTTPException
        raise HTTPException(403, "No tienes acceso a esta notificación")
    return notification

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    return await notification_service.mark_as_read(notification_id, user)

@router.post("/mark-multiple-read")
async def mark_multiple_read(
    payload: NotificationMarkRead,
    user: dict = Depends(get_current_user)
):
    """Mark multiple notifications as read"""
    return await notification_service.mark_multiple_as_read(payload, user)

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Delete notification"""
    return await notification_service.delete_notification(notification_id, user)

@router.get("/preferences")
async def get_preferences(
    user: dict = Depends(get_current_user)
):
    """Get notification preferences"""
    from app.services.notification_service import NotificationService
    notif_service = NotificationService()
    return await notif_service.get_user_preferences(user["id"])

@router.patch("/preferences")
async def update_preferences(
    preferences: dict,
    user: dict = Depends(get_current_user)
):
    """Update notification preferences"""
    from app.services.notification_service import NotificationService
    from app.core.supabase import table
    
    prefs_table = table("preferencias_notificaciones")
    
    # Actualizar o crear preferencias
    result = prefs_table.update(preferences) \
        .eq("usuario_id", user["id"]) \
        .execute()
    
    if result.data:
        return result.data[0]
    
    # Si no existe, crear nuevo
    new_prefs = {
        "usuario_id": user["id"],
        **preferences
    }
    result = prefs_table.insert(new_prefs).execute()
    return result.data[0] if result.data else None