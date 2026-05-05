from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class Voting(BaseModel):
    id: Optional[UUID]
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    opciones: List[str]
    estado: str = "activa"  # activa, finalizada, cancelada
    creado_por: UUID
    imagen_url: Optional[str] = None
    created_at: Optional[datetime] = None

class VotingCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    opciones: List[str]

class Vote(BaseModel):
    id: Optional[UUID]
    votacion_id: UUID
    usuario_id: UUID
    opcion: str
    created_at: Optional[datetime] = None

class VotingResponse(BaseModel):
    id: UUID
    titulo: str
    descripcion: Optional[str]
    fecha_inicio: datetime
    fecha_fin: datetime
    opciones: List[str]
    estado: str
    creado_por: UUID
    creado_por_nombre: str
    imagen_url: Optional[str]
    total_votos: int = 0
    resultados: dict = {}
    ya_voto: bool = False
    created_at: datetime

class VoteResponse(BaseModel):
    id: UUID
    votacion_id: UUID
    usuario_id: UUID
    opcion: str
    created_at: datetime