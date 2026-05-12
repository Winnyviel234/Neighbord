from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.core.supabase import execute_sql, table
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/notifications", tags=["notifications"])


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
    novedades: bool | None = None
    email_votaciones: bool | None = None
    email_reuniones: bool | None = None
    email_pagos: bool | None = None
    email_solicitudes: bool | None = None
    email_comunicados: bool | None = None
    email_directiva: bool | None = None
    email_chat: bool | None = None


def _ensure_tables():
    sql = """
    CREATE TABLE IF NOT EXISTS public.notificaciones (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        usuario_id UUID NOT NULL,
        titulo TEXT NOT NULL,
        contenido TEXT,
        tipo TEXT DEFAULT 'general',
        referencia_id UUID,
        referencia_tipo TEXT,
        leida BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS public.preferencias_notificaciones (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        usuario_id UUID NOT NULL UNIQUE,
        votaciones BOOLEAN DEFAULT TRUE,
        reuniones BOOLEAN DEFAULT TRUE,
        pagos BOOLEAN DEFAULT TRUE,
        solicitudes BOOLEAN DEFAULT TRUE,
        comunicados BOOLEAN DEFAULT TRUE,
        directiva BOOLEAN DEFAULT FALSE,
        chat BOOLEAN DEFAULT FALSE,
        novedades BOOLEAN DEFAULT TRUE,
        email_votaciones BOOLEAN DEFAULT TRUE,
        email_reuniones BOOLEAN DEFAULT TRUE,
        email_pagos BOOLEAN DEFAULT TRUE,
        email_solicitudes BOOLEAN DEFAULT FALSE,
        email_comunicados BOOLEAN DEFAULT TRUE,
        email_directiva BOOLEAN DEFAULT FALSE,
        email_chat BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON public.notificaciones(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_preferencias_notificaciones_usuario ON public.preferencias_notificaciones(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_notificaciones_leida ON public.notificaciones(leida);
    """
    try:
        execute_sql(sql)
    except Exception:
        pass


def _get_default_prefs(user_id: str) -> dict:
    return {
        "usuario_id": user_id,
        "votaciones": True,
        "reuniones": True,
        "pagos": True,
        "solicitudes": True,
        "comunicados": True,
        "directiva": False,
        "chat": False,
        "novedades": True,
        "email_votaciones": True,
        "email_reuniones": True,
        "email_pagos": True,
        "email_solicitudes": False,
        "email_comunicados": True,
        "email_directiva": False,
        "email_chat": False
    }


@router.get("/preferences")
async def get_preferences(user: dict = Depends(get_current_user)):
    """Get current user's notification preferences"""
    _ensure_tables()
    try:
        result = table("preferencias_notificaciones").select("*").eq("usuario_id", str(user["id"])).execute()
        if result.data:
            return result.data[0]
    except Exception:
        pass
    return _get_default_prefs(str(user["id"]))


@router.patch("/preferences")
async def update_preferences(
    payload: NotificationPreferencesUpdate,
    user: dict = Depends(get_current_user)
):
    """Update current user's notification preferences"""
    _ensure_tables()
    try:
        data = {"usuario_id": str(user["id"]), **payload.model_dump(exclude_none=True)}
        result = table("preferencias_notificaciones").upsert(data, on_conflict="usuario_id").execute()
        return result.data[0] if result.data else data
    except Exception:
        return _get_default_prefs(str(user["id"]))


@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    _ensure_tables()
    try:
        query = table("notificaciones").select("*").eq("usuario_id", str(user["id"])).order("created_at", desc=True).limit(limit)
        if unread_only:
            query = query.eq("leida", False)
        result = query.execute()
        return result.data or []
    except Exception:
        return []


@router.get("/unread/count")
async def get_unread_count(
    user: dict = Depends(get_current_user)
):
    """Get unread notifications count"""
    _ensure_tables()
    try:
        result = table("notificaciones").select("id", count="exact").eq("usuario_id", str(user["id"])).eq("leida", False).execute()
        return {"unread_count": result.count or 0}
    except Exception:
        return {"unread_count": 0}


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    _ensure_tables()
    try:
        result = table("notificaciones").update({"leida": True}).eq("id", str(notification_id)).eq("usuario_id", str(user["id"])).execute()
        return result.data[0] if result.data else {"message": "Actualizado"}
    except Exception:
        return {"message": "Actualizado"}


@router.post("/mark-multiple-read")
async def mark_multiple_read(
    user: dict = Depends(get_current_user)
):
    """Mark all unread notifications as read"""
    _ensure_tables()
    try:
        result = table("notificaciones").update({"leida": True}).eq("usuario_id", str(user["id"])).eq("leida", False).execute()
        return {"message": f"Marcadas {len(result.data or [])} notificaciones como leídas"}
    except Exception:
        return {"message": "Actualizado"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Delete notification"""
    _ensure_tables()
    try:
        result = table("notificaciones").delete().eq("id", str(notification_id)).eq("usuario_id", str(user["id"])).execute()
        return {"message": "Eliminado"}
    except Exception:
        return {"message": "Eliminado"}


@router.post("/whatsapp/test")
def send_whatsapp_test(payload: WhatsAppTestRequest, user: dict = Depends(get_current_user)):
    """Enviar un mensaje WhatsApp de prueba usando la configuración de Twilio"""
    service = WhatsAppService()
    if not service.enabled:
        return {"whatsapp_enabled": False, "result": {"sent": False, "detail": "WhatsApp no está configurado."}}
    result = service.send_message(payload.telefono, payload.mensaje)
    return {"whatsapp_enabled": service.enabled, "result": result}
