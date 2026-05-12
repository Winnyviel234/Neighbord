from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from time import time

from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/noticias", tags=["noticias"])
_CACHE = {"at": 0.0, "data": None}
CACHE_SECONDS = 60


def _add_image(data: dict, imagen: UploadFile | None) -> dict:
    if imagen:
        url = upload_to_storage(imagen, "neighborhood-images")
        if url:
            data["imagen_url"] = url
    return data


@router.get("")
def list_noticias(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros")
):
    now = time()
    if _CACHE["data"] is not None and now - _CACHE["at"] < CACHE_SECONDS:
        data = _CACHE["data"]
        return data[skip:skip + limit]
    
    data = table("noticias").select("*").eq("publicado", True).order("created_at", desc=True).limit(100).execute().data
    _CACHE.update({"at": now, "data": data})
    return data[skip:skip + limit]


@router.post("/form")
async def create_noticia_form(
    titulo: str = Form(...),
    resumen: str = Form(...),
    contenido: str = Form(...),
    publicado: bool = Form(True),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(get_current_user)
):
    data = {
        "titulo": titulo,
        "resumen": resumen,
        "contenido": contenido,
        "publicado": publicado,
        "autor_id": user["id"]
    }
    data = _add_image(data, imagen)
    created = table("noticias").insert(data).execute().data[0]
    if publicado:
        try:
            notifier = NotificationService()
            recipients = await notifier.get_active_recipients()
            await notifier.notify_noticia(created, recipients)
        except Exception:
            pass
    _CACHE.update({"at": 0.0, "data": None})
    return created


@router.get("/admin")
def list_noticias_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    user: dict = Depends(require_roles("admin"))
):
    query = table("noticias").select("*").order("created_at", desc=True).offset(skip).limit(limit)
    return query.execute().data


@router.patch("/{noticia_id}/form")
def update_noticia_form(
    noticia_id: str,
    titulo: str = Form(None),
    resumen: str = Form(None),
    contenido: str = Form(None),
    publicado: bool = Form(None),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin"))
):
    data = {}
    if titulo is not None: data["titulo"] = titulo
    if resumen is not None: data["resumen"] = resumen
    if contenido is not None: data["contenido"] = contenido
    if publicado is not None: data["publicado"] = publicado
    data = _add_image(data, imagen)
    if not data:
        return {"detail": "No data to update"}
    updated = table("noticias").update(data).eq("id", noticia_id).execute().data[0]
    _CACHE.update({"at": 0.0, "data": None})
    return updated


@router.delete("/{noticia_id}")
def delete_noticia(noticia_id: str, user: dict = Depends(require_roles("admin"))):
    deleted = table("noticias").delete().eq("id", noticia_id).execute().data[0]
    _CACHE.update({"at": 0.0, "data": None})
    return deleted


@router.get("/{noticia_id}/comments")
def list_noticia_comments(noticia_id: str):
    """
    Lista los comentarios de una noticia específica.
    """
    return table("noticia_comments").select("*, usuarios(nombre)").eq("noticia_id", noticia_id).order("created_at", desc=False).execute().data


@router.post("/{noticia_id}/comments")
def create_noticia_comment(
    noticia_id: str,
    contenido: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """
    Agrega un nuevo comentario a una noticia.
    """
    data = {
        "noticia_id": noticia_id,
        "usuario_id": user["id"],
        "contenido": contenido
    }
    return table("noticia_comments").insert(data).execute().data[0]


@router.delete("/comments/{comment_id}")
def delete_noticia_comment(comment_id: str, user: dict = Depends(get_current_user)):
    """
    Elimina un comentario (solo el autor o un admin).
    """
    existing = table("noticia_comments").select("*").eq("id", comment_id).execute().data
    if not existing:
        return {"detail": "Comentario no encontrado"}
    comment = existing[0]
    is_owner = comment["usuario_id"] == user["id"]
    is_admin = user.get("rol") in ["admin", "directiva"]
    if not is_owner and not is_admin:
        return {"detail": "No autorizado"}
    return table("noticia_comments").delete().eq("id", comment_id).execute().data[0]
