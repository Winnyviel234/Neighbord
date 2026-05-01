from fastapi import APIRouter
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.core.security import get_current_user, require_roles, has_role
from app.core.supabase import table, upload_to_storage
from app.schemas.schemas import ReunionCreate, Reunion

router = APIRouter(prefix="/reuniones", tags=["reuniones"])

def _add_image(data: dict, imagen: UploadFile | None) -> dict:
    if imagen:
        url = upload_to_storage(imagen, "neighborhood-images")
        if url:
            data["imagen_url"] = url
    return data

@router.get("/", response_model=list[Reunion])
def list_reuniones(tipo: str | None = None, user: dict = Depends(get_current_user)):
    """Obtiene todas las reuniones, opcionalmente filtradas por tipo."""
    query = table("reuniones").select("*").order("fecha", desc=True)
    if tipo:
        query = query.eq("tipo", tipo)
    if user["rol"] == "vecino":
        query = query.eq("tipo", "general")
    return [Reunion(**reunion) for reunion in query.execute().data]

@router.post("/form", response_model=Reunion, status_code=status.HTTP_201_CREATED)
def create_reunion_form(
    titulo: str = Form(...),
    descripcion: str = Form(None),
    fecha: str = Form(...),
    lugar: str = Form(...),
    tipo: str = Form("general"),
    estado: str = Form("programada"),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin", "directiva"))
):
    """
    Crea una nueva reunión a través de un formulario, con soporte para imagen.
    Solo usuarios con rol 'admin' o 'directiva' pueden crear reuniones.
    """
    # Parsear fecha: acepta ISO format
    try:
        # Remover 'Z' y parsear como ISO
        fecha_str = fecha.replace('Z', '+00:00') if fecha else None
        if not fecha_str:
            raise HTTPException(status_code=400, detail="Fecha es requerida")
        
        fecha_dt = datetime.fromisoformat(fecha_str)
    except (ValueError, TypeError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido. Recibido: {fecha}. Error: {str(e)}")
    
    reunion_data = {
        "titulo": titulo,
        "descripcion": descripcion or "",
        "fecha": fecha_dt.isoformat(),
        "lugar": lugar,
        "tipo": tipo,
        "estado": estado,
        "creado_por": user["id"]
    }
    reunion_data = _add_image(reunion_data, imagen)
    try:
        result = table("reuniones").insert(reunion_data).execute()
        return Reunion(**result.data[0])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar reunion: {str(e)}")



@router.patch("/{reunion_id}/form")
def update_reunion_form(
    reunion_id: str,
    titulo: str = Form(None),
    descripcion: str = Form(None),
    fecha: str = Form(None),
    lugar: str = Form(None),
    tipo: str = Form(None),
    estado: str = Form(None),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin"))
):
    data = {}
    if titulo is not None: data["titulo"] = titulo
    if descripcion is not None: data["descripcion"] = descripcion
    if fecha is not None:
        try:
            try:
                fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                fecha_dt = datetime.fromisoformat(fecha)
            data["fecha"] = fecha_dt.isoformat()
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {str(e)}")
    if lugar is not None: data["lugar"] = lugar
    if tipo is not None: data["tipo"] = tipo
    if estado is not None: data["estado"] = estado
    data = _add_image(data, imagen)
    if not data:
        return {"detail": "No data to update"}
    return table("reuniones").update(data).eq("id", reunion_id).execute().data[0]


@router.delete("/{reunion_id}")
def delete_reunion(reunion_id: str, user: dict = Depends(require_roles("admin"))):
    return table("reuniones").delete().eq("id", reunion_id).execute().data[0]


@router.post("/{reunion_id}/asistencia")
def asistencia(reunion_id: str, user: dict = Depends(get_current_user)):
    data = {"reunion_id": reunion_id, "usuario_id": user["id"]}
    return table("asistencias").upsert(data, on_conflict="reunion_id,usuario_id").execute().data[0]

@router.get("/{reunion_id}", response_model=Reunion) # Se mantuvo de la sugerencia anterior
def get_reunion_by_id(reunion_id: str, user: dict = Depends(get_current_user)):
    """
    Obtiene una reunión por su ID.
    """
    result = table("reuniones").select("*").eq("id", reunion_id).single().execute()
    return Reunion(**result.data)
