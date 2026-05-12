from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from typing import Optional
from uuid import UUID
from datetime import datetime

class Notification(BaseModel):
    id: Optional[UUID]
    usuario_id: UUID = Field(validation_alias=AliasChoices("usuario_id", "user_id"))
    titulo: str
    contenido: str = Field(validation_alias=AliasChoices("contenido", "mensaje"))
    tipo: str = "info"  # info, warning, error, success
    leida: bool = False
    referencia_id: Optional[UUID] = None  # ID del objeto relacionado (complaint, meeting, etc)
    referencia_tipo: Optional[str] = None  # Tipo del objeto (complaint, meeting, vote, etc)
    created_at: Optional[datetime] = None

class NotificationCreate(BaseModel):
    titulo: str
    contenido: str = Field(validation_alias=AliasChoices("contenido", "mensaje"))
    tipo: str = "info"
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None

class NotificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    usuario_id: UUID = Field(validation_alias=AliasChoices("usuario_id", "user_id"))
    titulo: str
    contenido: str = Field(validation_alias=AliasChoices("contenido", "mensaje"))
    tipo: str
    leida: bool
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None
    created_at: datetime

class NotificationMarkRead(BaseModel):
    ids: list[UUID]  # IDs de notificaciones a marcar como leídas
