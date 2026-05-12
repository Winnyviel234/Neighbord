from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from urllib.parse import quote

from fastapi import HTTPException
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.auth.repository import AuthRepository
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, PasswordResetConfirmRequest, PasswordResetRequest, ProfileUpdateRequest
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
        
        role_name = user.get("role_name", user.get("rol", "vecino"))
        if role_name not in ["admin", "superadmin"] and user.get("estado") not in ["aprobado", "activo"]:
            raise HTTPException(403, "Tu cuenta aún no está aprobada")
        
        # Create token with role info
        token_data = {
            "sub": str(user["id"]),
            "role": role_name,
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

    def _hash_reset_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def request_password_reset(self, data: PasswordResetRequest) -> Dict[str, Any]:
        """Send a one-time password reset link without revealing if the email exists."""
        generic = {"message": "Si el correo existe, enviaremos un enlace para recuperar la contrasena."}
        user = await self.repo.get_by_email(data.email)
        if not user or not user.get("activo", True):
            return generic

        token = secrets.token_urlsafe(48)
        token_hash = self._hash_reset_token(token)
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        await self.repo.create_password_reset_token(str(user["id"]), token_hash, expires_at)

        reset_url = f"{settings.frontend_url.rstrip('/')}/restablecer-contrasena?token={quote(token)}"
        email_result = self.email_service.password_reset(user["email"], user.get("nombre") or "vecino", reset_url)
        if not email_result.get("sent"):
            return {**generic, "email_configured": False, "detail": email_result.get("detail")}
        return generic

    async def reset_password(self, data: PasswordResetConfirmRequest) -> Dict[str, Any]:
        token_hash = self._hash_reset_token(data.token)
        token_row = await self.repo.get_password_reset_token(token_hash)
        if not token_row or token_row.get("used_at"):
            raise HTTPException(400, "El enlace no es valido o ya fue usado")

        expires_at = datetime.fromisoformat(str(token_row["expires_at"]).replace("Z", "+00:00"))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(400, "El enlace expiro. Solicita uno nuevo")

        await self.repo.update(token_row["usuario_id"], {"password_hash": hash_password(data.password_nueva)})
        await self.repo.mark_password_reset_used(token_row["id"], datetime.now(timezone.utc).isoformat())
        return {"message": "Contrasena actualizada. Ya puedes iniciar sesion."}
