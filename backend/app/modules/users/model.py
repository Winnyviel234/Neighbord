from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class User(BaseModel):
    id: Optional[UUID]
    nombre: str
    email: EmailStr
    telefono: Optional[str]
    direccion: Optional[str]
    documento: Optional[str]
    sector_id: Optional[UUID]
    role_id: UUID
    estado: str = "pendiente"
    activo: bool = True

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    documento: Optional[str] = None
    sector_id: Optional[UUID] = None

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None
    activo: Optional[bool] = None
    sector_id: Optional[UUID] = None
    role_id: Optional[UUID] = None

class UserResponse(BaseModel):
    id: UUID
    nombre: str
    email: EmailStr
    telefono: Optional[str]
    direccion: Optional[str]
    documento: Optional[str]
    sector_name: Optional[str]
    role_name: str
    estado: str
    activo: bool