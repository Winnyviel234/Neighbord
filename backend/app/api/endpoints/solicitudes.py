from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_roles
from app.core.supabase import table
from app.schemas.schemas import SolicitudIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.get("")
def list_solicitudes(user: dict = Depends(get_current_user)):
    query = table("solicitudes").select("*, usuarios(nombre,email)").order("created_at", desc=True)
    if user["rol"] == "vecino":
        query = query.eq("usuario_id", user["id"])
    return query.execute().data


@router.post("")
def create_solicitud(payload: SolicitudIn, user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    data.update({"usuario_id": user["id"], "estado": "abierta"})
    return table("solicitudes").insert(data).execute().data[0]


@router.patch("/{solicitud_id}/estado/{estado}")
def update_estado(solicitud_id: str, estado: str, user: dict = Depends(require_roles("admin", "directiva"))):
    updated = table("solicitudes").update({"estado": estado}).eq("id", solicitud_id).execute().data[0]
    owner = table("usuarios").select("email").eq("id", updated["usuario_id"]).single().execute().data
    if owner and owner.get("email"):
        EmailService().request_status(owner["email"], updated["titulo"], estado)
    return updated


@router.patch("/{solicitud_id}")
def update_solicitud(solicitud_id: str, payload: SolicitudIn, user: dict = Depends(require_roles("admin"))):
    return table("solicitudes").update(payload.model_dump()).eq("id", solicitud_id).execute().data[0]


@router.delete("/{solicitud_id}")
def delete_solicitud(solicitud_id: str, user: dict = Depends(require_roles("admin"))):
    return table("solicitudes").delete().eq("id", solicitud_id).execute().data[0]
