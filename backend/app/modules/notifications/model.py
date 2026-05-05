from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class NotificationBase(BaseModel):
    titulo: str
    contenido: str = Field(..., alias='mensaje')
    tipo: str = 'info'
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    leida: bool = Field(False, alias='read')
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

class NotificationMarkRead(BaseModel):
    ids: list[UUID]  # IDs de notificaciones a marcar como leídas
