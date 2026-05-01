from fastapi import APIRouter, Depends

from app.core.security import require_roles
from app.core.supabase import table
from app.schemas.schemas import VecinoIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/vecinos", tags=["vecinos"])


@router.get("")
def list_vecinos(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("usuarios").select("id,nombre,email,telefono,direccion,documento,rol,estado,activo,created_at").eq("activo", True).order("created_at", desc=True).execute().data


@router.post("")
def create_vecino(payload: VecinoIn, user: dict = Depends(require_roles("admin", "directiva"))):
    data = payload.model_dump()
    data.update({"rol": "vecino", "password_hash": "", "activo": True})
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
    return table("usuarios").update({"rol": rol}).eq("id", vecino_id).execute().data[0]


@router.patch("/{vecino_id}")
def update_vecino(vecino_id: str, payload: VecinoIn, user: dict = Depends(require_roles("admin"))):
    return table("usuarios").update(payload.model_dump()).eq("id", vecino_id).execute().data[0]


@router.delete("/{vecino_id}")
def delete_vecino(vecino_id: str, user: dict = Depends(require_roles("admin"))):
    return table("usuarios").update({"activo": False, "estado": "inactivo"}).eq("id", vecino_id).execute().data[0]


@router.get("/morosos")
def morosos(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("vista_morosos").select("*").execute().data
