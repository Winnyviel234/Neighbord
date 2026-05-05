from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    nombre: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    sector: str


class PasswordChangeIn(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=6, max_length=72)


class ProfileUpdateIn(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    documento: Optional[str] = None


class VecinoIn(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: str
    documento: Optional[str] = None
    estado: str = "pendiente"


class ReunionCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime
    lugar: str
    tipo: str = "general"
    estado: str = "programada"


class Reunion(BaseModel):
    id: str
    titulo: str
    descripcion: Optional[str] = None
    fecha: datetime
    lugar: str
    tipo: str
    estado: str
    creado_por: Optional[str] = None
    imagen_url: Optional[str] = None


class VotacionIn(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    opciones: list[str]
    estado: str = "activa"


class VotoIn(BaseModel):
    opcion: str


class PagoIn(BaseModel):
    vecino_id: str
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str = "efectivo"
    referencia: Optional[str] = None


class PagoCuotaIn(BaseModel):
    monto: float
    fecha_pago: date
    metodo: str = "transferencia"
    referencia: Optional[str] = None


class TransaccionIn(BaseModel):
    tipo: str
    categoria: str
    descripcion: str
    monto: float
    fecha: date


class SolicitudIn(BaseModel):
    titulo: str
    descripcion: str
    categoria: str = "general"
    prioridad: str = "media"


class ComunicadoIn(BaseModel):
    titulo: str
    contenido: str
    categoria: str = "general"
    publicado: bool = True


class NoticiaIn(BaseModel):
    titulo: str
    resumen: str
    contenido: str
    imagen_url: Optional[str] = None
    publicado: bool = True


class DirectivaIn(BaseModel):
    usuario_id: Optional[str] = None
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    cargo: str
    periodo: str
    activo: bool = True


class CuotaIn(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    monto: float
    fecha_vencimiento: date
    estado: str = "activa"


class EmailIn(BaseModel):
    destinatarios: list[EmailStr]
    asunto: str
    mensaje: str
