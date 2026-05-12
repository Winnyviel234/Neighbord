from typing import List, Optional, Dict, Any
from uuid import UUID
import httpx
from app.core.supabase import execute_sql, table

class NotificationRepository:
    def __init__(self):
        self.notifications_table = table("notificaciones")
        self.preferences_table = table("preferencias_notificaciones")
    
    def _ensure_preferences_table(self) -> None:
        """Create the preferences table if it does not exist."""
        create_table_sql = """
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
            updated_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_preferencias_notificaciones_usuario_id ON public.preferencias_notificaciones(usuario_id);
        ALTER TABLE public.preferencias_notificaciones ADD COLUMN IF NOT EXISTS novedades BOOLEAN DEFAULT TRUE;
        """
        execute_sql(create_table_sql)

    def get_user_notifications(self, user_id: UUID, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = self.notifications_table.select("*").eq("usuario_id", str(user_id))
        
        if unread_only:
            query = query.eq("leida", False)
        
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    def get_user_preferences(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get or create notification preferences for a user"""
        try:
            result = self.preferences_table.select("*").eq("usuario_id", str(user_id)).execute()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self._ensure_preferences_table()
                return None
            raise

        if result.data:
            return result.data[0]
        return None

    def save_user_preferences(self, user_id: UUID, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update notification preferences for a user"""
        data = {"usuario_id": str(user_id), **prefs}
        try:
            result = self.preferences_table.upsert(data, on_conflict="usuario_id").execute()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                self._ensure_preferences_table()
                result = self.preferences_table.upsert(data, on_conflict="usuario_id").execute()
            elif exc.response.status_code == 400 and "novedades" in data:
                try:
                    self._ensure_preferences_table()
                    result = self.preferences_table.upsert(data, on_conflict="usuario_id").execute()
                except Exception:
                    data.pop("novedades", None)
                    result = self.preferences_table.upsert(data, on_conflict="usuario_id").execute()
            else:
                raise
        return result.data[0] if result.data else data
    
    def get_by_id(self, notification_id: UUID) -> Optional[Dict[str, Any]]:
        """Get notification by ID"""
        result = self.notifications_table.select("*").eq("id", str(notification_id)).single().execute()
        return result.data
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification"""
        insert_data = dict(data)
        if "user_id" in insert_data and "usuario_id" not in insert_data:
            insert_data["usuario_id"] = insert_data.pop("user_id")
        result = self.notifications_table.insert(insert_data).execute()
        return result.data[0]
    
    def mark_as_read(self, notification_id: UUID) -> Optional[Dict[str, Any]]:
        """Mark notification as read"""
        result = self.notifications_table.update({"leida": True}).eq("id", str(notification_id)).execute()
        return result.data[0] if result.data else None
    
    def mark_multiple_as_read(self, notification_ids: List[UUID]) -> bool:
        """Mark multiple notifications as read"""
        if not notification_ids:
            return False
        id_strings = [str(nid) for nid in notification_ids]
        # Using in_ filter for multiple IDs
        query = self.notifications_table
        for nid in id_strings:
            query = query.or_(f"id.eq.{nid}")
        
        result = query.update({"leida": True}).execute()
        return len(result.data) > 0

    def mark_all_as_read(self, user_id: UUID) -> bool:
        """Mark all unread notifications for a user as read"""
        result = self.notifications_table.update({"leida": True}) \
            .eq("usuario_id", str(user_id)) \
            .eq("leida", False) \
            .execute()
        return len(result.data or []) > 0
    
    def delete(self, notification_id: UUID) -> bool:
        """Delete notification"""
        result = self.notifications_table.delete().eq("id", str(notification_id)).execute()
        return len(result.data) > 0
    
    def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications"""
        result = self.notifications_table.select("id", count="exact").eq("usuario_id", str(user_id)).eq("leida", False).execute()
        return result.count or 0
