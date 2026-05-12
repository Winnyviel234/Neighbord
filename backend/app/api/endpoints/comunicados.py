from fastapi import APIRouter, Depends, Form

from app.core.security import get_current_user, require_roles
from app.core.supabase import table
from app.schemas.schemas import ComunicadoIn
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/comunicados", tags=["comunicados"])


@router.get("")
def list_comunicados(user: dict = Depends(get_current_user)):
    return table("comunicados").select("*").order("created_at", desc=True).execute().data


@router.post("")
async def create_comunicado(payload: ComunicadoIn, user: dict = Depends(require_roles("admin"))):
    data = payload.model_dump()
    data["autor_id"] = user["id"]
    created = table("comunicados").insert(data).execute().data[0]
    try:
        notifier = NotificationService()
        recipients = await notifier.get_active_recipients()
        await notifier.notify_comunicado(created, recipients)
    except Exception:
        pass
    return created


@router.patch("/{comunicado_id}")
def update_comunicado(comunicado_id: str, payload: ComunicadoIn, user: dict = Depends(require_roles("admin"))):
    return table("comunicados").update(payload.model_dump()).eq("id", comunicado_id).execute().data[0]


@router.delete("/{comunicado_id}")
def delete_comunicado(comunicado_id: str, user: dict = Depends(require_roles("admin"))):
    return table("comunicados").delete().eq("id", comunicado_id).execute().data[0]

@router.get("/{comunicado_id}/comments")
def list_comunicado_comments(comunicado_id: str):
    """
    Lista los comentarios de un comunicado específico.
    """
    return table("comunicado_comments").select("*, usuarios(nombre)").eq("comunicado_id", comunicado_id).order("created_at", desc=False).execute().data

@router.post("/{comunicado_id}/comments")
def create_comunicado_comment(
    comunicado_id: str,
    contenido: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """
    Agrega un nuevo comentario a un comunicado.
    """
    data = {
        "comunicado_id": comunicado_id,
        "usuario_id": user["id"],
        "contenido": contenido
    }
    return table("comunicado_comments").insert(data).execute().data[0]
