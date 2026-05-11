from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
import csv

from app.core.security import require_roles
from app.core.supabase import table
from app.services.email_service import EmailService
from app.services.report_service import ReportFactory

router = APIRouter(prefix="/reportes", tags=["reportes"])

TABLES = {
    "vecinos": "usuarios",
    "financiero": "transacciones",
    "solicitudes": "solicitudes",
    "actas": "reuniones",
    "cronograma": "reuniones",
}

# Limite de filas por lote para evitar sobrecarga
MAX_ROWS_PER_BATCH = 1000


def stream_csv(rows: list[dict], columns: list[str], filename: str):
    """Genera CSV en streaming para evitar cargar todo en memoria"""
    def generate():
        output = BytesIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        
        # Escribir header
        writer.writeheader()
        output.seek(0)
        yield output.getvalue()
        
        # Escribir filas en lotes
        for row in rows:
            output = BytesIO()
            writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
            writer.writerow(row)
            output.seek(0)
            yield output.getvalue()
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{tipo}.{formato}")
def download_report(
    tipo: str,
    formato: str,
    limit: int = Query(5000, description="Límite de filas a descargar"),
    user: dict = Depends(require_roles("admin", "directiva", "tesorero"))
):
    if tipo not in TABLES or formato not in ["pdf", "csv", "xlsx"]:
        raise HTTPException(status_code=404, detail="Reporte no disponible")
    
    # Aplicar límite para evitar cargar demasiados datos
    query = table(TABLES[tipo]).select("*").limit(limit)
    rows = query.execute().data
    
    if not rows:
        raise HTTPException(status_code=404, detail="No hay datos para este reporte")
    
    report = ReportFactory.create(tipo, rows)
    
    if formato == "csv":
        # Usar streaming para CSV
        return stream_csv(rows, report.columns, f"{tipo}.csv")
    
    if formato == "pdf":
        # Para PDF se mantiene igual (PDFs pequeños generalmente)
        return Response(
            report.to_pdf(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={tipo}.pdf"}
        )


@router.post("/email/mora/{usuario_id}")
def send_mora(usuario_id: str, monto: float, user: dict = Depends(require_roles("admin", "tesorero"))):
    vecino = table("usuarios").select("email").eq("id", usuario_id).single().execute().data
    if not vecino:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    return EmailService().debt_alert(vecino["email"], monto)

