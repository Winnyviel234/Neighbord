from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user, require_roles
from app.core.supabase import table
from app.schemas.schemas import SolicitudIn
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.get("")
def list_solicitudes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=1000, description="Número máximo de registros"),
    user: dict = Depends(get_current_user)
):
    query = table("solicitudes").select("*, usuarios(nombre,email)").order("created_at", desc=True)
    if user["rol"] == "vecino":
        query = query.eq("usuario_id", user["id"])
    
    # Aplicar paginación
    query = query.offset(skip).limit(limit)
    data = query.execute().data
    
    # También obtener el total para el frontend
    total_query = table("solicitudes").select("id", count="exact")
    if user["rol"] == "vecino":
        total_query = total_query.eq("usuario_id", user["id"])
    total = total_query.execute().count
    
    return {
        "data": data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("")
async def create_solicitud(payload: SolicitudIn, user: dict = Depends(get_current_user)):
    data = payload.model_dump()
    data.update({"usuario_id": user["id"], "estado": "pendiente"})
    created = table("solicitudes").insert(data).execute().data[0]
    notif_service = NotificationService()
    await notif_service.notify_solicitud(str(user["id"]), {
        **created,
        "titulo": created.get("titulo", ""),
        "categoria": created.get("categoria", ""),
        "estado": "pendiente"
    })
    return created


@router.patch("/{solicitud_id}/estado/{estado}")
async def update_estado(solicitud_id: str, estado: str, user: dict = Depends(require_roles("admin", "directiva"))):
    updated = table("solicitudes").update({"estado": estado}).eq("id", solicitud_id).execute().data[0]
    owner = table("usuarios").select("email").eq("id", updated["usuario_id"]).single().execute().data
    if owner and owner.get("email"):
        EmailService().request_status(owner["email"], updated["titulo"], estado)
    notif_service = NotificationService()
    await notif_service.notify_solicitud(str(updated["usuario_id"]), {
        **updated,
        "titulo": updated.get("titulo", ""),
        "categoria": updated.get("categoria", ""),
        "estado": estado
    })
    return updated


@router.patch("/{solicitud_id}")
def update_solicitud(solicitud_id: str, payload: SolicitudIn, user: dict = Depends(require_roles("admin"))):
    return table("solicitudes").update(payload.model_dump()).eq("id", solicitud_id).execute().data[0]


@router.delete("/{solicitud_id}")
def delete_solicitud(solicitud_id: str, user: dict = Depends(require_roles("admin"))):
    return table("solicitudes").delete().eq("id", solicitud_id).execute().data[0]
