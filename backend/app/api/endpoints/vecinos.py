from fastapi import APIRouter, Depends, HTTPException

from app.core.security import hash_password, require_roles
from app.core.supabase import table
from app.schemas.schemas import VecinoIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/vecinos", tags=["vecinos"])


@router.get("")
def list_vecinos(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("usuarios").select("id,nombre,email,telefono,direccion,documento,rol,estado,activo,created_at").eq("activo", True).order("created_at", desc=True).execute().data


@router.post("")
def create_vecino(payload: VecinoIn, user: dict = Depends(require_roles("admin", "directiva"))):
    data = payload.model_dump(exclude_none=True)
    password = data.pop("password", None)
    if not password:
        raise HTTPException(status_code=400, detail="Debes especificar una contraseña para el vecino")
    data["password_hash"] = hash_password(password)
    data.update({"rol": "vecino", "activo": True})
    return table("usuarios").insert(data).execute().data[0]


@router.patch("/{vecino_id}/aprobar")
def approve_vecino(vecino_id: str, user: dict = Depends(require_roles("admin", "directiva"))):
    updated = table("usuarios").update({"estado": "aprobado"}).eq("id", vecino_id).execute().data[0]
    if updated.get("email"):
        EmailService().account_approved(updated["email"], updated["nombre"])
    return updated


@router.patch("/{vecino_id}/estado/{estado}")
def update_estado(vecino_id: str, estado: str, user: dict = Depends(require_roles("admin", "directiva"))):
    return table("usuarios").update({"estado": estado}).eq("id", vecino_id).execute().data[0]


@router.patch("/{vecino_id}/rol/{rol}")
def update_rol(vecino_id: str, rol: str, user: dict = Depends(require_roles("admin"))):
    allowed_roles = {"vecino", "directiva", "tesorero", "vocero", "secretaria"}
    if rol not in allowed_roles:
        raise HTTPException(status_code=400, detail="No se puede asignar ese rol desde aquí")
    return table("usuarios").update({"rol": rol}).eq("id", vecino_id).execute().data[0]


@router.patch("/{vecino_id}")
def update_vecino(vecino_id: str, payload: VecinoIn, user: dict = Depends(require_roles("admin"))):
    return table("usuarios").update(payload.model_dump()).eq("id", vecino_id).execute().data[0]


@router.delete("/{vecino_id}")
def delete_vecino(vecino_id: str, user: dict = Depends(require_roles("admin"))):
    target = table("usuarios").select("id,rol").eq("id", vecino_id).single().execute().data
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if target.get("rol") == "admin":
        raise HTTPException(status_code=403, detail="No se puede eliminar una cuenta de administrador")
    if target.get("id") == user["id"]:
        raise HTTPException(status_code=403, detail="No puedes eliminar tu propia cuenta de administrador")
    return table("usuarios").update({"activo": False, "estado": "inactivo"}).eq("id", vecino_id).execute().data[0]


@router.get("/morosos")
def morosos(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("vista_morosos").select("*").execute().data
