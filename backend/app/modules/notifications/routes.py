from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.notifications.service import NotificationService
from app.modules.notifications.model import NotificationMarkRead
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/notifications", tags=["notifications"])

notification_service = NotificationService()


class WhatsAppTestRequest(BaseModel):
    telefono: str
    mensaje: str

class NotificationPreferencesUpdate(BaseModel):
    votaciones: bool | None = None
    reuniones: bool | None = None
    pagos: bool | None = None
    solicitudes: bool | None = None
    comunicados: bool | None = None
    directiva: bool | None = None
    chat: bool | None = None
    email_votaciones: bool | None = None
    email_reuniones: bool | None = None
    email_pagos: bool | None = None
    email_solicitudes: bool | None = None
    email_comunicados: bool | None = None
    email_directiva: bool | None = None
    email_chat: bool | None = None

@router.get("/preferences")
async def get_preferences(user: dict = Depends(get_current_user)):
    """Get current user's notification preferences"""
    return await notification_service.get_user_preferences(user["id"])

@router.patch("/preferences")
async def update_preferences(
    payload: NotificationPreferencesUpdate,
    user: dict = Depends(get_current_user)
):
    """Update current user's notification preferences"""
    updated = await notification_service.save_user_preferences(user["id"], payload.dict(exclude_none=True))
    return updated

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


@router.post("/whatsapp/test")
def send_whatsapp_test(payload: WhatsAppTestRequest, user: dict = Depends(get_current_user)):
    """Enviar un mensaje WhatsApp de prueba usando la configuración de Twilio"""
    service = WhatsAppService()
    if not service.enabled:
        return {"whatsapp_enabled": False, "result": {"sent": False, "detail": "WhatsApp no está configurado."}}
    result = service.send_message(payload.telefono, payload.mensaje)
    return {"whatsapp_enabled": service.enabled, "result": result}
