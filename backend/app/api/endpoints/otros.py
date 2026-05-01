from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_roles
from app.core.supabase import table

router = APIRouter(tags=["otros"])


@router.get("/dashboard")
def dashboard(user: dict = Depends(get_current_user)):
    solicitudes_query = table("solicitudes").select("*").order("created_at", desc=True)
    pagos_query = table("pagos_cuotas").select("*").order("fecha_pago", desc=True)
    if user["rol"] == "vecino":
        solicitudes_query = solicitudes_query.eq("usuario_id", user["id"])
        pagos_query = pagos_query.eq("vecino_id", user["id"])

    solicitudes = solicitudes_query.limit(5).execute().data
    pagos = pagos_query.limit(5).execute().data
    reuniones = table("reuniones").select("*").order("fecha", desc=True).limit(5).execute().data
    votaciones_activas = table("votaciones").select("*").eq("estado", "activa").order("created_at", desc=True).limit(5).execute().data
    
    # Add stats to votaciones activas
    for v in votaciones_activas:
        votos = table("votos").select("opcion").eq("votacion_id", v["id"]).execute().data
        conteo = {}
        for vt in votos:
            opcion = vt["opcion"]
            conteo[opcion] = conteo.get(opcion, 0) + 1
        total = len(votos)
        v["total_votos"] = total
        v["opciones_stats"] = [
            {"opcion": opcion, "count": conteo.get(opcion, 0), "percentage": round((conteo.get(opcion, 0) / total) * 100, 1) if total > 0 else 0}
            for opcion in (v.get("opciones") or [])
        ]
    
    comunicados = table("comunicados").select("*").eq("publicado", True).order("created_at", desc=True).limit(5).execute().data
    noticias = table("noticias").select("*").eq("publicado", True).order("created_at", desc=True).limit(5).execute().data
    cuotas = table("cuotas").select("*").eq("estado", "activa").order("fecha_vencimiento").limit(5).execute().data

    return {
        "vecinos": len(table("usuarios").select("id").eq("activo", True).execute().data),
        "solicitudes": len(table("solicitudes").select("id").execute().data),
        "reuniones": len(table("reuniones").select("id").execute().data),
        "votaciones": len(table("votaciones").select("id").eq("estado", "activa").execute().data),
        "pagos": len(table("pagos_cuotas").select("id").execute().data),
        "rol": user["rol"],
        "resumen": {
            "comunidad": "Sistema comunitario activo",
            "estado": "Conectado a datos reales",
        },
        "ultimos_anuncios": [*comunicados, *noticias][:5],
        "reportes_recientes": solicitudes,
        "eventos_proximos": reuniones,
        "votaciones_activas": votaciones_activas,
        "cuotas_activas": cuotas,
        "pagos_recientes": pagos,
        "notificaciones": [
            {"titulo": "Reportes", "mensaje": f"{len(solicitudes)} reportes recientes para revisar"},
            {"titulo": "Votaciones", "mensaje": f"{len(votaciones_activas)} votaciones activas disponibles"},
            {"titulo": "Pagos", "mensaje": f"{len(cuotas)} cuotas activas en la comunidad"},
        ],
    }


@router.get("/public/landing")
def public_landing():
    comunicados = table("comunicados").select("*").eq("publicado", True).order("created_at", desc=True).limit(5).execute().data
    noticias = table("noticias").select("*").eq("publicado", True).order("created_at", desc=True).limit(5).execute().data
    votaciones = table("votaciones").select("*").eq("estado", "activa").order("created_at", desc=True).limit(5).execute().data
    
    # Add stats to votaciones
    for v in votaciones:
        votos = table("votos").select("opcion").eq("votacion_id", v["id"]).execute().data
        conteo = {}
        for vt in votos:
            opcion = vt["opcion"]
            conteo[opcion] = conteo.get(opcion, 0) + 1
        total = len(votos)
        v["total_votos"] = total
        v["opciones_stats"] = [
            {"opcion": opcion, "count": conteo.get(opcion, 0), "percentage": round((conteo.get(opcion, 0) / total) * 100, 1) if total > 0 else 0}
            for opcion in (v.get("opciones") or [])
        ]
    
    asambleas = table("reuniones").select("*").eq("tipo", "general").eq("estado", "programada").order("fecha", desc=True).limit(5).execute().data
    directiva = table("directiva").select("*").eq("activo", True).order("cargo").execute().data
    
    return {
        "comunicados": comunicados,
        "noticias": noticias,
        "votaciones": votaciones,
        "asambleas": asambleas,
        "directiva": directiva
    }


@router.get("/proyectos")
def proyectos(user: dict = Depends(get_current_user)):
    return table("proyectos").select("*").order("created_at", desc=True).execute().data


@router.get("/auditoria")
def auditoria(user: dict = Depends(require_roles("admin"))):
    return table("auditoria").select("*").order("created_at", desc=True).limit(100).execute().data
