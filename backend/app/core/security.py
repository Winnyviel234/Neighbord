from datetime import datetime, timedelta, timezone
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.supabase import table

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(payload: dict) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {**payload, "exp": expires}
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
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
    return result.data


def require_roles(*roles: Iterable[str]):
    allowed = set(roles)

    def dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in allowed:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user

    return dependency


def has_role(user: dict, roles: list[str]) -> bool:
    """
    Verifica si el usuario tiene alguno de los roles especificados.
    """
    return user.get("rol") in roles
