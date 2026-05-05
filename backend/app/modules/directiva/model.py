from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CargoCreate(BaseModel):
    """DTO for creating a directiva position"""
    name: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=10, max_length=500)
    permisos: List[str] = []  # Special permissions for this role
    sector_id: UUID


class CargoUpdate(BaseModel):
    """DTO for updating a directiva position"""
    name: Optional[str] = None
    descripcion: Optional[str] = None
    permisos: Optional[List[str]] = None


class CargoAsignacion(BaseModel):
    """DTO for assigning a person to a cargo"""
    user_id: UUID
    cargo_id: UUID
    sector_id: UUID
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None


class CargoAsignacionUpdate(BaseModel):
    """DTO for updating cargo assignment"""
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = None


class CargoResponse(BaseModel):
    """DTO for cargo responses"""
    id: UUID
    name: str
    descripcion: str
    sector_id: UUID
    permisos: List[str]
    created_at: datetime
    updated_at: datetime


class CargoAsignacionResponse(BaseModel):
    """DTO for cargo assignment responses"""
    id: UUID
    user_id: UUID
    cargo_id: UUID
    sector_id: UUID
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    activo: bool
    created_at: datetime


class DirectivaResponse(BaseModel):
    """DTO for complete directiva view"""
    sector_id: UUID
    miembros: List[dict]  # List of users with their cargos
    created_at: datetime


# Default cargos for new sectors
DEFAULT_CARGOS = [
    {
        "name": "Presidente",
        "descripcion": "Representa a la junta directiva. Convoca asambleas, firma documentos.",
        "permisos": ["manage_all", "convoke_assemblies", "sign_documents", "manage_directiva"]
    },
    {
        "name": "Vice-Presidente",
        "descripcion": "Reemplaza al presidente en ausencia. Apoya en gestión general.",
        "permisos": ["manage_all", "convoke_assemblies", "manage_directiva"]
    },
    {
        "name": "Secretario",
        "descripcion": "Registra actas de reuniones. Gestiona comunicaciones oficiales.",
        "permisos": ["manage_communications", "manage_meetings", "manage_documents"]
    },
    {
        "name": "Tesorero",
        "descripcion": "Gestiona finanzas, pagos y presupuesto de la comunidad.",
        "permisos": ["manage_finances", "approve_expenses", "view_reports", "manage_budget"]
    },
    {
        "name": "Vocal",
        "descripcion": "Apoya en gestión general. Participa en decisiones directivas.",
        "permisos": ["participate_decisions", "manage_documents", "view_reports"]
    }
]
