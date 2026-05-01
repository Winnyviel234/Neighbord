from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form
from time import time

from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage

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
def list_noticias():
    now = time()
    if _CACHE["data"] is not None and now - _CACHE["at"] < CACHE_SECONDS:
        return _CACHE["data"]
    data = table("noticias").select("*").eq("publicado", True).order("created_at", desc=True).limit(20).execute().data
    _CACHE.update({"at": now, "data": data})
    return data


@router.post("/form")
def create_noticia_form(
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
    _CACHE.update({"at": 0.0, "data": None})
    return created


@router.get("/admin")
def list_noticias_admin(user: dict = Depends(require_roles("admin"))):
    return table("noticias").select("*").order("created_at", desc=True).limit(100).execute().data


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
