from fastapi import APIRouter, Depends, HTTPException

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.core.supabase import table
from app.schemas.schemas import LoginIn, PasswordChangeIn, ProfileUpdateIn, RegisterIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterIn):
    existing = table("usuarios").select("id").eq("email", payload.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Este correo ya está registrado")

    user = {
        "nombre": payload.nombre,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "telefono": payload.telefono,
        "direccion": payload.direccion,
        "documento": payload.documento,
        "rol": "vecino",
        "estado": "pendiente",
        "activo": True,
    }
    created = table("usuarios").insert(user).execute().data[0]
    EmailService().welcome(payload.email, payload.nombre)
    return {"message": "Registro creado. Espera aprobación de la directiva.", "user": created}


@router.post("/login")
def login(payload: LoginIn):
    result = table("usuarios").select("*").eq("email", payload.email).single().execute()
    user = result.data
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if user.get("estado") not in ["aprobado", "activo"]:
        raise HTTPException(status_code=403, detail="Tu cuenta aún no está aprobada")
    token = create_access_token({"sub": user["id"], "role": user["rol"]})
    user.pop("password_hash", None)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    user.pop("password_hash", None)
    return user


@router.patch("/me")
def update_me(payload: ProfileUpdateIn, user: dict = Depends(get_current_user)):
    updated = table("usuarios").update(payload.model_dump()).eq("id", user["id"]).execute().data[0]
    updated.pop("password_hash", None)
    return updated


@router.post("/change-password")
def change_password(payload: PasswordChangeIn, user: dict = Depends(get_current_user)):
    if not verify_password(payload.password_actual, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    table("usuarios").update({"password_hash": hash_password(payload.password_nueva)}).eq("id", user["id"]).execute()
    return {"message": "Contraseña actualizada"}
