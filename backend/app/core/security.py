from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.supabase import table
from app.modules.auth.repository import DEFAULT_ROLES, DEFAULT_SECTOR

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(payload: dict) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {**payload, "exp": expires}
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _resolve_user_role(user: dict) -> tuple[str, list[str]]:
    role_name = user.get("rol", "vecino")
    role_permissions = DEFAULT_ROLES.get(role_name, DEFAULT_ROLES["vecino"])["permissions"]
    if user.get("role_id"):
        try:
            role_result = table("roles").select("name, permissions").eq("id", user["role_id"]).single().execute()
            if role_result.data:
                role_name = role_result.data.get("name", role_name)
                role_permissions = role_result.data.get("permissions", role_permissions)
        except Exception:
            pass

    super_email = settings.super_admin_email or settings.admin_email
    if super_email and str(user.get("email", "")).strip().lower() == str(super_email).strip().lower():
        role_name = "superadmin"
        role_permissions = DEFAULT_ROLES["superadmin"]["permissions"]

    return role_name, role_permissions


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    approval_error = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Tu cuenta aún no está aprobada",
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc

    result = table("usuarios").select("*").eq("id", user_id).single().execute()
    if not result.data or not result.data.get("activo", True):
        raise credentials_error

    user = result.data
    role_name, role_permissions = _resolve_user_role(user)

    if user.get("estado") not in ["aprobado", "activo"] and role_name not in ["admin", "superadmin"]:
        raise approval_error

    sector_name = DEFAULT_SECTOR["name"]
    if user.get("sector_id"):
        try:
            sector_result = table("sectors").select("name").eq("id", user["sector_id"]).single().execute()
            if sector_result.data:
                sector_name = sector_result.data.get("name", sector_name)
        except Exception:
            pass

    user["role_name"] = role_name
    user["role_permissions"] = role_permissions
    user["sector_name"] = sector_name
    return user


def get_optional_current_user(token: str | None = Depends(oauth2_optional_scheme)) -> dict | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    result = table("usuarios").select("*").eq("id", user_id).single().execute()
    if not result.data or not result.data.get("activo", True):
        return None

    user = result.data
    role_name, role_permissions = _resolve_user_role(user)

    if user.get("estado") not in ["aprobado", "activo"] and role_name not in ["admin", "superadmin"]:
        return None

    sector_name = DEFAULT_SECTOR["name"]
    if user.get("sector_id"):
        try:
            sector_result = table("sectors").select("name").eq("id", user["sector_id"]).single().execute()
            if sector_result.data:
                sector_name = sector_result.data.get("name", sector_name)
        except Exception:
            pass

    user["role_name"] = role_name
    user["role_permissions"] = role_permissions
    user["sector_name"] = sector_name
    return user


def require_permissions(*required_permissions: str):
    """
    Dependency that requires specific permissions.
    Checks if user has any of the required permissions in their role.
    """
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        user_permissions = user.get("role_permissions", [])
        if not user_permissions:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        
        # Check if user has 'all' permission or any required permission
        if "all" in user_permissions:
            return user
        
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        
        return user
    
    return dependency


def require_roles(*roles: Iterable[str]):
    """
    Legacy dependency for backward compatibility.
    Use require_permissions instead for new code.
    """
    allowed = set(roles)

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role_name") == "superadmin":
            return user
        if user.get("role_name") not in allowed:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user

    return dependency


# Compatibility alias for older code paths
require_role = require_roles


def has_role(user: dict, roles: list[str]) -> bool:
    """
    Verifica si el usuario tiene alguno de los roles especificados.
    """
    if user.get("role_name") == "superadmin":
        return True
    return user.get("role_name") in roles
