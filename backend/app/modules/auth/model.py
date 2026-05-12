import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr, validator

class RegisterRequest(BaseModel):
    nombre: constr(strip_whitespace=True, min_length=3)
    email: EmailStr
    password: str
    telefono: Optional[str] = None
    direccion: Optional[constr(strip_whitespace=True, min_length=5)] = None
    documento: Optional[constr(strip_whitespace=True, min_length=3)] = None
    sector_id: Optional[str] = Field(default=None, alias='sector')

    class Config:
        validate_by_name = True
        str_strip_whitespace = True

    @validator('telefono', pre=True, always=True)
    def normalize_phone(cls, value):
        if value is None or value == '':
            return None
        cleaned = re.sub(r'[^\d+]', '', value)
        if len(cleaned) < 8 or len(cleaned) > 15:
            raise ValueError('Teléfono inválido')
        if not cleaned.startswith('+'):
            cleaned = f'+{cleaned}'
        return cleaned

    @validator('*', pre=True)
    def sanitize_strings(cls, value):
        if isinstance(value, str):
            return re.sub(r'<[^>]+>', '', value).strip()
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    password_actual: str
    password_nueva: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    password_nueva: str = Field(min_length=6, max_length=72)

class ProfileUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
