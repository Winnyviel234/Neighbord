from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    titulo: str
    contenido: str
    tipo: str
    referencia_id: Optional[str] = None
    referencia_tipo: Optional[str] = None

class NotificationCreate(NotificationBase):
    usuario_id: str

class NotificationUpdate(BaseModel):
    leida: bool

class NotificationResponse(NotificationBase):
    id: str
    usuario_id: str
    leida: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PreferenciasNotificacionesBase(BaseModel):
    votaciones: bool = True
    reuniones: bool = True
    pagos: bool = True
    solicitudes: bool = True
    comunicados: bool = True
    directiva: bool = False
    chat: bool = False
    email_votaciones: bool = True
    email_reuniones: bool = True
    email_pagos: bool = True
    email_solicitudes: bool = False
    email_comunicados: bool = True
    email_directiva: bool = False
    email_chat: bool = False

class PreferenciasNotificacionesUpdate(BaseModel):
    votaciones: Optional[bool] = None
    reuniones: Optional[bool] = None
    pagos: Optional[bool] = None
    solicitudes: Optional[bool] = None
    comunicados: Optional[bool] = None
    directiva: Optional[bool] = None
    chat: Optional[bool] = None
    email_votaciones: Optional[bool] = None
    email_reuniones: Optional[bool] = None
    email_pagos: Optional[bool] = None
    email_solicitudes: Optional[bool] = None
    email_comunicados: Optional[bool] = None
    email_directiva: Optional[bool] = None
    email_chat: Optional[bool] = None

class PreferenciasNotificacionesResponse(PreferenciasNotificacionesBase):
    usuario_id: str

    class Config:
        from_attributes = True
