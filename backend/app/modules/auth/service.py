from fastapi import HTTPException
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.repository import AuthRepository
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest
from app.modules.sectors.repository import SectorRepository
from app.services.email_service import EmailService
from app.core.audit_helper import audit_login, audit_create
from typing import Dict, Any
from uuid import UUID

class AuthService:
    def __init__(self):
        self.repo = AuthRepository()
        self.email_service = EmailService()
    
    async def register(self, data: RegisterRequest) -> Dict[str, Any]:
        """Register new user"""
        # Check if email exists
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(409, "Este correo ya está registrado")
        
        # Prepare user data
        user_data = {
            "nombre": data.nombre,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "telefono": data.telefono,
            "direccion": data.direccion,
            "estado": "pendiente",
            "activo": True
        }
        
        if not data.sector or not data.sector.strip():
            raise HTTPException(400, "Debes especificar el sector de tu barrio")

        sector_name = data.sector.strip()
        sector_repo = SectorRepository()
        sector = await sector_repo.get_by_name(sector_name)
        if not sector:
            sector = await sector_repo.create({"name": sector_name})

        user_data["sector_id"] = sector["id"]
        
        # Create user
        try:
            user = await self.repo.create(user_data)
        except RuntimeError as exc:
            raise HTTPException(500, str(exc)) from exc
        
        # Audit log registration
        await audit_create(
            resource_type="users",
            resource_id=UUID(user["id"]),
            new_values=user_data,
            user_id=UUID(user["id"])
        )
        
        # Send welcome email
        try:
            self.email_service.welcome(data.email, data.nombre)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Error sending welcome email: {e}")
        
        return {
            "message": "Registro creado. Espera aprobación de la directiva.",
            "user_id": user["id"]
        }
    
    async def login(self, data: LoginRequest) -> Dict[str, Any]:
        """Authenticate user"""
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(401, "Credenciales inválidas")
        
        if user.get("estado") not in ["aprobado", "activo", "pendiente"]:
            raise HTTPException(403, "Tu cuenta aún no está aprobada")
        
        # Ensure frontend compatibility: use both `rol` and `role_name` fields
        if not user.get("rol") and user.get("role_name"):
            user["rol"] = user["role_name"]
        
        # Create token with role info
        token_data = {
            "sub": str(user["id"]),
            "role": user.get("role_name", user.get("rol", "vecino")),
            "sector_id": str(user.get("sector_id")) if user.get("sector_id") else None
        }
        token = create_access_token(token_data)
        
        # Audit log login
        await audit_login(user_id=UUID(user["id"]))
        
        # Remove sensitive data
        user.pop("password_hash", None)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
    
    async def get_current_user(self, user_id: str) -> Dict[str, Any]:
        """Get current user profile"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        user.pop("password_hash", None)
        return user
    
    async def update_profile(self, user_id: str, data: ProfileUpdateRequest) -> Dict[str, Any]:
        """Update user profile"""
        update_data = data.model_dump(exclude_unset=True)
        user = await self.repo.update(user_id, update_data)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        user.pop("password_hash", None)
        return user
    
    async def change_password(self, user_id: str, data: PasswordChangeRequest) -> Dict[str, Any]:
        """Change user password"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "Usuario no encontrado")
        
        if not verify_password(data.password_actual, user["password_hash"]):
            raise HTTPException(400, "Contraseña actual incorrecta")
        
        new_hash = hash_password(data.password_nueva)
        await self.repo.update(user_id, {"password_hash": new_hash})
        
        return {"message": "Contraseña actualizada"}