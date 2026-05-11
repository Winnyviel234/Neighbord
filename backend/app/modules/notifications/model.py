from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Notification(BaseModel):
    id: Optional[UUID]
    user_id: UUID
    titulo: str
    mensaje: str
    tipo: str = "info"  # info, warning, error, success
    leida: bool = False
    referencia_id: Optional[UUID] = None  # ID del objeto relacionado (complaint, meeting, etc)
    referencia_tipo: Optional[str] = None  # Tipo del objeto (complaint, meeting, vote, etc)
    created_at: Optional[datetime] = None

class NotificationCreate(BaseModel):
    titulo: str
    mensaje: str
    tipo: str = "info"
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    titulo: str
    mensaje: str
    tipo: str
    leida: bool
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None
    created_at: datetime

class NotificationMarkRead(BaseModel):
    ids: list[UUID]  # IDs de notificaciones a marcar como leídas