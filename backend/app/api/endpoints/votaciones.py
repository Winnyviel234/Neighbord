from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from httpx import HTTPStatusError
from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage
from app.schemas.schemas import VotacionIn, VotoIn
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/votaciones", tags=["votaciones"])

def _parse_election_option(option: str) -> dict[str, str]:
    parts = option.split("|")
    if not parts or parts[0] != "election":
        return {}
    values = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")
        values[key] = value
    return values

def _is_election(votacion: dict) -> bool:
    return any(_parse_election_option(option) for option in votacion.get("opciones") or [])

def _add_stats(votacion: dict) -> dict:
    votos = table("votos").select("opcion").eq("votacion_id", votacion["id"]).execute().data or []
    conteo = {}
    for vt in votos:
        opcion = vt["opcion"]
        conteo[opcion] = conteo.get(opcion, 0) + 1
    total = len(votos)
    votacion["total_votos"] = total
    opciones = votacion.get("opciones") or []
    votacion["opciones_stats"] = [
        {
            "opcion": opcion,
            "count": conteo.get(opcion, 0),
            "percentage": round((conteo.get(opcion, 0) / total) * 100, 1) if total > 0 else 0
        }
        for opcion in opciones
    ]
    return votacion

def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

def _finish_election(votacion_id: str) -> dict:
    votacion = table("votaciones").select("*").eq("id", votacion_id).single().execute().data
    if not votacion:
        raise HTTPException(status_code=404, detail="Votacion no encontrada")
    if not _is_election(votacion):
        raise HTTPException(status_code=400, detail="Esta votacion no es una eleccion")
    
    votos = table("votos").select("opcion").eq("votacion_id", votacion_id).execute().data or []
    if not votos:
        raise HTTPException(status_code=400, detail="No hay votos registrados")
    
    conteo: dict[str, int] = {}
    for voto in votos:
        opcion = voto.get("opcion")
        conteo[opcion] = conteo.get(opcion, 0) + 1
    
    max_votos = max(conteo.values())
    ganadores = [opcion for opcion, total in conteo.items() if total == max_votos]
    if len(ganadores) > 1:
        raise HTTPException(status_code=409, detail="La eleccion termino empatada")
    
    ganador = ganadores[0]
    datos = _parse_election_option(ganador)
    usuario_id = datos.get("user")
    rol = datos.get("role")
    if rol not in {"directiva", "tesorero", "admin", "vecino"} or not usuario_id:
        raise HTTPException(status_code=400, detail="Opcion ganadora invalida")
    
    usuario = table("usuarios").update({"rol": rol, "estado": "aprobado", "activo": True}).eq("id", usuario_id).execute().data[0]
    table("votaciones").update({"estado": "cerrada"}).eq("id", votacion_id).execute()
    return {"ganador": usuario, "rol_asignado": rol, "votos": max_votos}

@router.get("")
def list_votaciones(user: dict = Depends(get_current_user)):
    votaciones = table("votaciones").select("*").order("created_at", desc=True).execute().data
    for v in votaciones:
        _add_stats(v)
    if votaciones:
        votacion_ids = [v["id"] for v in votaciones if v.get("id")]
        votos_usuario = table("votos").select("votacion_id, opcion").eq("usuario_id", user["id"]).in_("votacion_id", votacion_ids).execute().data or []
        votos_por_id = {v["votacion_id"]: v["opcion"] for v in votos_usuario if v.get("votacion_id")}
        for v in votaciones:
            if v.get("id") in votos_por_id:
                v["mi_voto"] = votos_por_id[v["id"]]
    return votaciones

@router.post("/form")
async def create_votacion_form(
    titulo: str = Form(...),
    descripcion: str = Form(None),
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    opciones: str = Form(...),
    estado: str = Form("activa"),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin", "directiva"))
):
    # Parsear fechas: acepta ISO format
    try:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido. Recibido: {fecha_inicio}, {fecha_fin}. Error: {str(e)}")
    
    data = {
        "titulo": titulo,
        "descripcion": descripcion or "",
        "fecha_inicio": fecha_inicio_dt.isoformat(),
        "fecha_fin": fecha_fin_dt.isoformat(),
        "opciones": [opcion.strip() for opcion in opciones.split(",") if opcion.strip()] if opciones else [],
        "estado": estado,
        "creado_por": user["id"]
    }
    if imagen:
        url = upload_to_storage(imagen, "neighborhood-images")
        if url:
            data["imagen_url"] = url
    try:
        created = table("votaciones").insert(data).execute().data[0]
        try:
            notifier = NotificationService()
            recipients = await notifier.get_active_recipients()
            await notifier.notify_votacion(created, recipients)
        except Exception:
            pass
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar votacion: {str(e)}")


@router.patch("/{votacion_id}/form")
async def update_votacion_form(
    votacion_id: str,
    titulo: str = Form(...),
    descripcion: str = Form(None),
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    opciones: str = Form(...),
    estado: str = Form("activa"),
    imagen: UploadFile | None = File(None),
    user: dict = Depends(require_roles("admin"))
):
    # Parsear fechas: acepta ISO format
    try:
        fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {str(e)}")
    
    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "fecha_inicio": fecha_inicio_dt.isoformat(),
        "fecha_fin": fecha_fin_dt.isoformat(),
        "opciones": [opcion.strip() for opcion in opciones.split(",") if opcion.strip()] if opciones else [],
        "estado": estado
    }
    if imagen:
        url = upload_to_storage(imagen, "neighborhood-images")
        if url:
            data["imagen_url"] = url
    return table("votaciones").update(data).eq("id", votacion_id).execute().data[0]

@router.delete("/{votacion_id}")
def delete_votacion(votacion_id: str, user: dict = Depends(require_roles("admin"))):
    return table("votaciones").delete().eq("id", votacion_id).execute().data[0]

@router.post("/{votacion_id}/votar")
def votar(votacion_id: str, payload: VotoIn, user: dict = Depends(get_current_user)):
    votacion = table("votaciones").select("estado, opciones, fecha_inicio, fecha_fin").eq("id", votacion_id).single().execute().data
    if not votacion:
        raise HTTPException(status_code=404, detail="Votacion no encontrada")
    if votacion.get("estado") != "activa":
        raise HTTPException(status_code=400, detail="La votacion no esta activa")
    ahora = datetime.now(timezone.utc)
    fecha_inicio = _parse_datetime(votacion.get("fecha_inicio"))
    fecha_fin = _parse_datetime(votacion.get("fecha_fin"))
    if fecha_inicio and ahora < fecha_inicio:
        raise HTTPException(status_code=400, detail="La votacion aun no ha iniciado")
    if fecha_fin and ahora > fecha_fin:
        raise HTTPException(status_code=400, detail="La votacion ya finalizo")
    if payload.opcion not in (votacion.get("opciones") or []):
        raise HTTPException(status_code=400, detail="Opcion invalida para esta votacion")
    voted = table("votos").select("id").eq("votacion_id", votacion_id).eq("usuario_id", user["id"]).execute()
    if voted.data:
        raise HTTPException(status_code=409, detail="Ya votaste en esta votacion")
    try:
        result = table("votos").insert({"votacion_id": votacion_id, "usuario_id": user["id"], "opcion": payload.opcion}).execute().data
    except HTTPStatusError as exc:
        if exc.response.status_code == 409 or "23505" in exc.response.text:
            raise HTTPException(status_code=409, detail="Ya votaste en esta votacion") from exc
        raise
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo registrar el voto")
    return result[0]

@router.delete("/{votacion_id}/votar")
def cancelar_voto(votacion_id: str, user: dict = Depends(get_current_user)):
    votacion = table("votaciones").select("estado").eq("id", votacion_id).single().execute().data
    if not votacion:
        raise HTTPException(status_code=404, detail="Votacion no encontrada")
    if votacion.get("estado") != "activa":
        raise HTTPException(status_code=400, detail="No se puede cancelar el voto en una votacion cerrada")
    deleted = table("votos").delete().eq("votacion_id", votacion_id).eq("usuario_id", user["id"]).execute()
    if not deleted.data:
        raise HTTPException(status_code=404, detail="No existe un voto para eliminar")
    return {"status": "ok"}

@router.post("/{votacion_id}/finalizar-eleccion")
def finalizar_eleccion(votacion_id: str, user: dict = Depends(require_roles("admin"))):
    return _finish_election(votacion_id)

@router.get("/{votacion_id}/resultados")
def resultados(votacion_id: str, user: dict = Depends(get_current_user)):
    votacion = table("votaciones").select("*").eq("id", votacion_id).single().execute().data
    if not votacion:
        raise HTTPException(status_code=404, detail="Votacion no encontrada")
    return _add_stats(votacion)
