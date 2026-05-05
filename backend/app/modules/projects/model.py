from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class ProjectCreate(BaseModel):
    """DTO for creating a new project"""
    sector_id: UUID
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    status: str = "planeado"  # planeado, en_progreso, completado, cancelado
    presupuesto_estimado: float = Field(..., gt=0)
    presupuesto_aprobado: Optional[float] = None
    fecha_inicio: date
    fecha_fin_estimada: date
    responsable_id: UUID
    prioridad: str = "media"  # baja, media, alta, crítica


class ProjectUpdate(BaseModel):
    """DTO for updating a project"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    presupuesto_aprobado: Optional[float] = None
    fecha_fin_estimada: Optional[date] = None
    responsable_id: Optional[UUID] = None
    prioridad: Optional[str] = None


class ProjectResponse(BaseModel):
    """DTO for project responses"""
    id: UUID
    sector_id: UUID
    title: str
    description: str
    status: str
    presupuesto_estimado: float
    presupuesto_aprobado: Optional[float]
    presupuesto_ejecutado: float = 0
    fecha_inicio: date
    fecha_fin_estimada: date
    fecha_fin_real: Optional[date]
    responsable_id: UUID
    prioridad: str
    progreso: int = 0  # 0-100
    created_at: datetime
    updated_at: datetime


class ProjectExpense(BaseModel):
    """DTO for project expenses"""
    id: Optional[UUID] = None
    project_id: UUID
    descripcion: str = Field(..., min_length=5, max_length=500)
    monto: float = Field(..., gt=0)
    fecha: date
    categoria: str  # materiales, mano_obra, permisos, otros
    comprobante_url: Optional[str]
    aprobado: bool = False
    created_at: Optional[datetime] = None
