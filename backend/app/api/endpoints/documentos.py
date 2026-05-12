from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/documentos", tags=["documentos"])


def _local_documents() -> list[dict]:
    base_dir = Path(__file__).resolve().parents[2] / "uploads" / "documentos"
    if not base_dir.exists():
        return []
    return [
        {
            "id": file.name,
            "titulo": file.name,
            "archivo_url": f"/uploads/documentos/{file.name}",
            "tipo": file.suffix.lstrip(".").lower() or "archivo",
            "origen": "local"
        }
        for file in sorted(base_dir.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True)
        if file.is_file()
    ]


@router.get("")
def list_documentos(user: dict = Depends(get_current_user)):
    try:
        rows = table("documentos").select("*").order("created_at", desc=True).execute().data or []
    except Exception:
        rows = []

    local_rows = _local_documents()
    known_urls = {row.get("archivo_url") for row in rows}
    rows.extend([row for row in local_rows if row.get("archivo_url") not in known_urls])
    return rows


@router.post("/form")
async def upload_documento(
    titulo: str = Form(...),
    descripcion: str = Form(None),
    archivo: UploadFile = File(...),
    user: dict = Depends(require_roles("admin", "directiva", "tesorero"))
):
    archivo_url = upload_to_storage(archivo, "documentos")
    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "archivo_url": archivo_url,
        "nombre_archivo": archivo.filename,
        "tipo": archivo.content_type,
        "subido_por": user["id"]
    }
    try:
        created = table("documentos").insert(data).execute().data[0]
    except Exception:
        data["id"] = Path(archivo_url or archivo.filename).name
        data["origen"] = "local"
        created = data
    try:
        notifier = NotificationService()
        recipients = await notifier.get_active_recipients()
        await notifier.notify_documento(created, recipients)
    except Exception:
        pass
    return created


@router.delete("/{documento_id}")
def delete_documento(
    documento_id: str,
    user: dict = Depends(require_roles("admin", "directiva", "tesorero"))
):
    local_dir = Path(__file__).resolve().parents[2] / "uploads" / "documentos"
    local_file = local_dir / Path(documento_id).name

    if local_file.exists() and local_file.is_file():
        local_file.unlink()
        return {"id": documento_id, "deleted": True, "origen": "local"}

    try:
        deleted = table("documentos").delete().eq("id", documento_id).execute().data
        if deleted:
            return deleted[0]
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Documento no encontrado")
