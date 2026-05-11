from fastapi import HTTPException
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.repository import AuthRepository
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest
from app.services.email_service import EmailService
from typing import Dict, Any

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
            "documento": data.documento,
            "estado": "pendiente",
            "activo": True
        }
        
        if data.sector_id:
            user_data["sector_id"] = data.sector_id
        
        # Create user
        user = await self.repo.create(user_data)
        
        # Send welcome email
        try:
            self.email_service.welcome(data.email, data.nombre)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Error sending welcome email: {e}")

        user.pop("password_hash", None)

        return {
            "message": "Registro creado. Te notificaremos cuando tu cuenta esté lista para usar.",
            "status": "pending_approval",
            "user": user
        }
    
    async def login(self, data: LoginRequest) -> Dict[str, Any]:
        """Authenticate user"""
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(401, "Credenciales inválidas")
        
        if user.get("rol") != "admin" and user.get("estado") not in ["aprobado", "activo"]:
            raise HTTPException(403, "Tu cuenta aún no está aprobada")
        
        # Create token with role info
        token_data = {
            "sub": str(user["id"]),
            "role": user.get("rol", "vecino"),
            "sector_id": str(user.get("sector_id")) if user.get("sector_id") else None
        }
        token = create_access_token(token_data)
        
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
