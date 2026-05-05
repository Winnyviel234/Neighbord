from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Meeting(BaseModel):
    id: Optional[UUID]
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime
    lugar: str
    tipo: str = "general"  # general, directiva
    estado: str = "programada"  # programada, activa, finalizada
    creado_por: UUID
    imagen_url: Optional[str] = None
    created_at: Optional[datetime] = None

class MeetingCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime
    lugar: str
    tipo: str = "general"

class MeetingUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha: Optional[datetime] = None
    lugar: Optional[str] = None
    estado: Optional[str] = None

class Attendance(BaseModel):
    id: Optional[UUID]
    reunion_id: UUID
    usuario_id: UUID
    created_at: Optional[datetime] = None

class MeetingResponse(BaseModel):
    id: UUID
    titulo: str
    descripcion: Optional[str]
    fecha: datetime
    lugar: str
    tipo: str
    estado: str
    creado_por: UUID
    creado_por_nombre: str
    imagen_url: Optional[str]
    asistentes: int = 0
    created_at: datetime

class AttendanceResponse(BaseModel):
    id: UUID
    reunion_id: UUID
    usuario_id: UUID
    usuario_nombre: str
    created_at: datetime