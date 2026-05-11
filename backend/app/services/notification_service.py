"""
Notification Service - Sistema de notificaciones por email
Maneja templates y envío de notificaciones para diferentes eventos
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.email_service import EmailService
from app.services.whatsapp_service import WhatsAppService
from app.core.supabase import table

class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()
        self.notifications_table = table("notificaciones")
        self.user_preferences_table = table("preferencias_notificaciones")

    async def save_notification(self, user_id: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Guardar notificación en la base de datos"""
        data = {
            "usuario_id": user_id,
            "tipo": notification_data.get("tipo"),
            "titulo": notification_data.get("titulo"),
            "contenido": notification_data.get("contenido"),
            "referencia_id": notification_data.get("referencia_id"),
            "referencia_tipo": notification_data.get("referencia_tipo"),
            "leida": False,
            "created_at": datetime.now().isoformat()
        }
        result = self.notifications_table.insert(data).execute()
        return result.data[0] if result.data else None

    async def get_user_preferences(self, user_id: str) -> Dict[str, bool]:
        """Obtener preferencias de notificación del usuario"""
        result = self.user_preferences_table.select("*").eq("usuario_id", user_id).execute()
        if result.data:
            return result.data[0]
        
        # Preferencias por defecto
        default_prefs = {
            "usuario_id": user_id,
            "votaciones": True,
            "reuniones": True,
            "pagos": True,
            "solicitudes": True,
            "comunicados": True,
            "directiva": True,
            "chat": True,
            "email_votaciones": True,
            "email_reuniones": True,
            "email_pagos": True,
            "email_solicitudes": False,
            "email_comunicados": True,
            "email_directiva": False,
            "email_chat": False
        }
        self.user_preferences_table.insert(default_prefs).execute()
        return default_prefs

    async def save_user_preferences(self, user_id: str, prefs: Dict[str, bool]) -> Dict[str, bool]:
        """Guardar o actualizar preferencias de notificación del usuario"""
        data = {"usuario_id": user_id}
        allowed_keys = [
            "votaciones", "reuniones", "pagos", "solicitudes", "comunicados", "directiva", "chat",
            "email_votaciones", "email_reuniones", "email_pagos", "email_solicitudes", "email_comunicados",
            "email_directiva", "email_chat"
        ]
        for key in allowed_keys:
            if key in prefs:
                data[key] = bool(prefs[key])

        result = self.user_preferences_table.upsert(data, on_conflict="usuario_id").execute()
        if result.data:
            return result.data[0]
        return data

    async def _get_user_phone(self, user_id: str) -> Optional[str]:
        users_table = table("usuarios")
        result = users_table.select("telefono").eq("id", user_id).execute()
        if result.data:
            return result.data[0].get("telefono")
        return None

    def _send_whatsapp(self, phones: List[str], title: str, content: str) -> Dict[str, Any]:
        if not self.whatsapp_service.enabled or not phones:
            return {"sent": 0, "detail": "WhatsApp no configurado o no hay destinatarios."}
        return self.whatsapp_service.send_bulk(phones, f"{title}\n\n{content}")

    def _notification_votacion(self, votacion_data: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificación de votación"""
        return {
            "titulo": f"Nueva votación: {votacion_data['titulo']}",
            "contenido": f"""
                <h3>{votacion_data['titulo']}</h3>
                <p>{votacion_data.get('descripcion', '')}</p>
                <div style="background: #e8f4f8; padding: 12px; border-radius: 8px; margin: 16px 0;">
                    <p><strong>Vence:</strong> {votacion_data.get('fecha_fin', 'Próximamente')}</p>
                    <p><strong>Opciones:</strong> {len(votacion_data.get('opciones', []))} opción(es)</p>
                </div>
                <p><a href="https://neighbord.app/app/votaciones" style="color: #0b5cab; text-decoration: none; font-weight: bold;">Ver votación →</a></p>
            """,
            "tipo": "votacion",
            "referencia_tipo": "votacion"
        }

    def _notification_reunion(self, reunion_data: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificación de reunión"""
        return {
            "titulo": f"Reunión programada: {reunion_data['titulo']}",
            "contenido": f"""
                <h3>{reunion_data['titulo']}</h3>
                <p>{reunion_data.get('descripcion', '')}</p>
                <div style="background: #e8f4f8; padding: 12px; border-radius: 8px; margin: 16px 0;">
                    <p><strong>Fecha:</strong> {reunion_data.get('fecha', '')}</p>
                    <p><strong>Hora:</strong> {reunion_data.get('hora', '')}</p>
                    <p><strong>Lugar:</strong> {reunion_data.get('lugar', '')}</p>
                </div>
                <p><a href="https://neighbord.app/app/reuniones" style="color: #0b5cab; text-decoration: none; font-weight: bold;">Ver detalles →</a></p>
            """,
            "tipo": "reunion",
            "referencia_tipo": "reunion"
        }

    def _notification_pago(self, pago_data: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificación de pago"""
        estado_color = {
            "completado": "#10b981",
            "pendiente": "#f59e0b",
            "rechazado": "#ef4444"
        }.get(pago_data.get("estado"), "#6b7280")
        
        return {
            "titulo": f"Pago {pago_data.get('estado', 'actualizado')}: {pago_data.get('concepto', 'Cuota')}",
            "contenido": f"""
                <h3>Actualización de Pago</h3>
                <div style="background: {estado_color}22; padding: 12px; border-radius: 8px; margin: 16px 0; border-left: 4px solid {estado_color};">
                    <p><strong style="color: {estado_color};">Estado:</strong> {pago_data.get('estado', '').upper()}</p>
                    <p><strong>Monto:</strong> ${pago_data.get('monto', 0)}</p>
                    <p><strong>Concepto:</strong> {pago_data.get('concepto', '')}</p>
                </div>
                <p><a href="https://neighbord.app/app/pagos" style="color: #0b5cab; text-decoration: none; font-weight: bold;">Ver mis pagos →</a></p>
            """,
            "tipo": "pago",
            "referencia_tipo": "pago"
        }

    def _notification_solicitud(self, solicitud_data: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificación de solicitud"""
        estado_color = {
            "resuelta": "#10b981",
            "pendiente": "#f59e0b",
            "en progreso": "#3b82f6"
        }.get(solicitud_data.get("estado"), "#6b7280")
        
        return {
            "titulo": f"Solicitud {solicitud_data.get('estado', 'actualizada')}: {solicitud_data.get('titulo', '')}",
            "contenido": f"""
                <h3>Actualización de Solicitud</h3>
                <p><strong>Asunto:</strong> {solicitud_data.get('titulo', '')}</p>
                <div style="background: {estado_color}22; padding: 12px; border-radius: 8px; margin: 16px 0; border-left: 4px solid {estado_color};">
                    <p><strong style="color: {estado_color};">Estado:</strong> {solicitud_data.get('estado', '').upper()}</p>
                    <p><strong>Categoría:</strong> {solicitud_data.get('categoria', '')}</p>
                </div>
                <p><a href="https://neighbord.app/app/solicitudes" style="color: #0b5cab; text-decoration: none; font-weight: bold;">Ver solicitud →</a></p>
            """,
            "tipo": "solicitud",
            "referencia_tipo": "solicitud"
        }

    def _notification_comunicado(self, comunicado_data: Dict[str, Any]) -> Dict[str, str]:
        """Template para notificación de comunicado"""
        return {
            "titulo": f"Nuevo comunicado: {comunicado_data.get('titulo', '')}",
            "contenido": f"""
                <h3>{comunicado_data.get('titulo', '')}</h3>
                <p>{comunicado_data.get('resumen', comunicado_data.get('contenido', ''))}</p>
                <div style="background: #e8f4f8; padding: 12px; border-radius: 8px; margin: 16px 0;">
                    <p><strong>Categoría:</strong> {comunicado_data.get('categoria', '')}</p>
                </div>
                <p><a href="https://neighbord.app/app/comunicados" style="color: #0b5cab; text-decoration: none; font-weight: bold;">Leer más →</a></p>
            """,
            "tipo": "comunicado",
            "referencia_tipo": "comunicado"
        }

    async def notify_votacion(self, votacion_data: Dict[str, Any], recipients: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Notificar sobre nueva votación"""
        notification = self._notification_votacion(votacion_data)
        
        # Guardar notificaciones individuales
        for recipient in recipients:
            prefs = await self.get_user_preferences(recipient["id"])
            if prefs.get("votaciones"):
                await self.save_notification(recipient["id"], {
                    **notification,
                    "referencia_id": votacion_data.get("id")
                })
        
        # Enviar emails
        if self.email_service.enabled:
            email_recipients = [r.get("email") for r in recipients if r.get("email")]
            if email_recipients:
                prefs_list = [await self.get_user_preferences(r["id"]) for r in recipients]
                filtered_emails = [
                    email_recipients[i] for i, prefs in enumerate(prefs_list)
                    if prefs.get("email_votaciones")
                ]
                if filtered_emails:
                    self.email_service.send(
                        filtered_emails,
                        notification["titulo"],
                        notification["contenido"]
                    )

        whatsapp_recipients = [r["telefono"] for r in recipients if r.get("telefono")]
        whatsapp_result = self._send_whatsapp(whatsapp_recipients, notification["titulo"], notification["contenido"])

        return {"sent": len(recipients), "type": "votacion", "whatsapp": whatsapp_result}

    async def notify_reunion(self, reunion_data: Dict[str, Any], recipients: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Notificar sobre nueva reunión"""
        notification = self._notification_reunion(reunion_data)
        
        for recipient in recipients:
            prefs = await self.get_user_preferences(recipient["id"])
            if prefs.get("reuniones"):
                await self.save_notification(recipient["id"], {
                    **notification,
                    "referencia_id": reunion_data.get("id")
                })
        
        if self.email_service.enabled:
            email_recipients = [r.get("email") for r in recipients if r.get("email")]
            if email_recipients:
                prefs_list = [await self.get_user_preferences(r["id"]) for r in recipients]
                filtered_emails = [
                    email_recipients[i] for i, prefs in enumerate(prefs_list)
                    if prefs.get("email_reuniones")
                ]
                if filtered_emails:
                    self.email_service.send(
                        filtered_emails,
                        notification["titulo"],
                        notification["contenido"]
                    )

        whatsapp_recipients = [r["telefono"] for r in recipients if r.get("telefono")]
        whatsapp_result = self._send_whatsapp(whatsapp_recipients, notification["titulo"], notification["contenido"])

        return {"sent": len(recipients), "type": "reunion", "whatsapp": whatsapp_result}

    async def notify_pago(self, user_id: str, pago_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notificar a usuario sobre actualización de pago"""
        notification = self._notification_pago(pago_data)
        
        prefs = await self.get_user_preferences(user_id)
        if prefs.get("pagos"):
            await self.save_notification(user_id, {
                **notification,
                "referencia_id": pago_data.get("id")
            })
        
        # Enviar email si está habilitado
        user_email = await self._get_user_email(user_id)
        if user_email and self.email_service.enabled and prefs.get("email_pagos"):
            self.email_service.send(
                [user_email],
                notification["titulo"],
                notification["contenido"]
            )

        phone = await self._get_user_phone(user_id)
        whatsapp_result = self._send_whatsapp([phone] if phone else [], notification["titulo"], notification["contenido"])

        return {"sent": 1, "type": "pago", "whatsapp": whatsapp_result}

    async def notify_solicitud(self, user_id: str, solicitud_data: Dict[str, Any]) -> Dict[str, Any]:
        """Notificar a usuario sobre cambio en solicitud"""
        notification = self._notification_solicitud(solicitud_data)
        
        prefs = await self.get_user_preferences(user_id)
        if prefs.get("solicitudes"):
            await self.save_notification(user_id, {
                **notification,
                "referencia_id": solicitud_data.get("id")
            })
        
        user_email = await self._get_user_email(user_id)
        if user_email and self.email_service.enabled and prefs.get("email_solicitudes"):
            self.email_service.send(
                [user_email],
                notification["titulo"],
                notification["contenido"]
            )

        phone = await self._get_user_phone(user_id)
        whatsapp_result = self._send_whatsapp([phone] if phone else [], notification["titulo"], notification["contenido"])

        return {"sent": 1, "type": "solicitud", "whatsapp": whatsapp_result}

    async def notify_comunicado(self, comunicado_data: Dict[str, Any], recipients: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Notificar sobre nuevo comunicado"""
        notification = self._notification_comunicado(comunicado_data)
        
        for recipient in recipients:
            prefs = await self.get_user_preferences(recipient["id"])
            if prefs.get("comunicados"):
                await self.save_notification(recipient["id"], {
                    **notification,
                    "referencia_id": comunicado_data.get("id")
                })
        
        if self.email_service.enabled:
            email_recipients = [r.get("email") for r in recipients if r.get("email")]
            if email_recipients:
                prefs_list = [await self.get_user_preferences(r["id"]) for r in recipients]
                filtered_emails = [
                    email_recipients[i] for i, prefs in enumerate(prefs_list)
                    if prefs.get("email_comunicados")
                ]
                if filtered_emails:
                    self.email_service.send(
                        filtered_emails,
                        notification["titulo"],
                        notification["contenido"]
                    )

        whatsapp_recipients = [r["telefono"] for r in recipients if r.get("telefono")]
        whatsapp_result = self._send_whatsapp(whatsapp_recipients, notification["titulo"], notification["contenido"])

        return {"sent": len(recipients), "type": "comunicado", "whatsapp": whatsapp_result}

    async def get_user_notifications(self, user_id: str, limit: int = 20) -> list[Dict[str, Any]]:
        """Obtener notificaciones del usuario"""
        result = self.notifications_table.select("*") \
            .eq("usuario_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data or []

    async def mark_as_read(self, notification_id: str) -> Dict[str, Any]:
        """Marcar notificación como leída"""
        result = self.notifications_table.update({"leida": True}) \
            .eq("id", notification_id) \
            .execute()
        return result.data[0] if result.data else None

    async def mark_all_as_read(self, user_id: str) -> Dict[str, Any]:
        """Marcar todas las notificaciones del usuario como leídas"""
        result = self.notifications_table.update({"leida": True}) \
            .eq("usuario_id", user_id) \
            .eq("leida", False) \
            .execute()
        return {"updated": len(result.data or [])}

    async def _get_user_email(self, user_id: str) -> Optional[str]:
        """Obtener email del usuario"""
        users_table = table("usuarios")
        result = users_table.select("email").eq("id", user_id).execute()
        if result.data:
            return result.data[0].get("email")
        return None
