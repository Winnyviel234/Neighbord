from fastapi import APIRouter

from app.core.supabase import table

router = APIRouter(prefix="/public", tags=["public"])


def _add_stats(votacion: dict) -> dict:
    """Calcula estadísticas de votos para una votación."""
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


@router.get("/comunicados")
def comunicados_publicos():
    return table("comunicados").select("*").eq("publicado", True).order("created_at", desc=True).limit(6).execute().data


@router.get("/landing")
def landing_publica():
    votaciones = table("votaciones").select("*").eq("estado", "activa").order("created_at", desc=True).limit(12).execute().data
    for v in votaciones:
        _add_stats(v)
    return {
        "comunicados": table("comunicados").select("*").eq("publicado", True).order("created_at", desc=True).limit(6).execute().data,
        "noticias": table("noticias").select("*").eq("publicado", True).order("created_at", desc=True).limit(6).execute().data,
        "votaciones": votaciones,
        "pagos": table("pagos").select("*").order("fecha_pago", desc=True).limit(6).execute().data,
        "asambleas": table("reuniones").select("*").eq("tipo", "general").order("fecha", desc=False).limit(6).execute().data,
        "directiva": table("directiva").select("*").eq("activo", True).order("cargo", desc=False).execute().data,
    }
