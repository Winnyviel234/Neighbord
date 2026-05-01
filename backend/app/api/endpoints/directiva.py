from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage

router = APIRouter(prefix="/directiva", tags=["directiva"])


def _add_image(data: dict, imagen: UploadFile | None) -> dict:
    if imagen:
        url = upload_to_storage(imagen, "neighborhood-images")
        if url:
            data["imagen_url"] = url
    return data


@router.get("")
def list_directiva(user: dict = Depends(get_current_user)):
    return table("directiva").select("*").eq("activo", True).order("cargo").execute().data


@router.post("/form")
def save_directivo_form(
    nombre: str = Form(...),
    email: str = Form(None),
    telefono: str = Form(None),
    cargo: str = Form(...),
    periodo: str = Form(...),
    activo: bool = Form(True),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin"))
):
    data = {
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "cargo": cargo,
        "periodo": periodo,
        "activo": activo
    }
    data = _add_image(data, imagen)
    return table("directiva").insert(data).execute().data[0]


@router.patch("/{directivo_id}/form")
def update_directivo_form(
    directivo_id: str,
    nombre: str = Form(None),
    email: str = Form(None),
    telefono: str = Form(None),
    cargo: str = Form(None),
    periodo: str = Form(None),
    activo: bool = Form(None),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin"))
):
    data = {}
    if nombre is not None: data["nombre"] = nombre
    if email is not None: data["email"] = email
    if telefono is not None: data["telefono"] = telefono
    if cargo is not None: data["cargo"] = cargo
    if periodo is not None: data["periodo"] = periodo
    if activo is not None: data["activo"] = activo
    data = _add_image(data, imagen)
    if not data:
        return {"detail": "No data to update"}
    return table("directiva").update(data).eq("id", directivo_id).execute().data[0]


@router.delete("/{directivo_id}")
def delete_directivo(directivo_id: str, user: dict = Depends(require_roles("admin"))):
    return table("directiva").update({"activo": False}).eq("id", directivo_id).execute().data[0]


@router.get("/reuniones")
def reuniones_directiva(user: dict = Depends(get_current_user)):
    return table("reuniones").select("*").eq("tipo", "directiva").order("fecha", desc=True).execute().data
