from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from io import StringIO
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


def stream_csv(rows: list[dict], columns: list[str], filename: str):
    def generate():
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        yield output.getvalue().encode("utf-8-sig")

        for row in rows:
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
            writer.writerow(row)
            yield output.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{tipo}.{formato}")
def download_report(
    tipo: str,
    formato: str,
    limit: int = Query(5000, description="Limite de filas a descargar"),
    user: dict = Depends(require_roles("admin", "directiva", "tesorero"))
):
    if tipo not in TABLES or formato not in ["pdf", "csv", "xlsx"]:
        raise HTTPException(status_code=404, detail="Reporte no disponible")

    rows = table(TABLES[tipo]).select("*").limit(limit).execute().data
    if not rows:
        raise HTTPException(status_code=404, detail="No hay datos para este reporte")

    report = ReportFactory.create(tipo, rows)

    if formato == "csv":
        return stream_csv(rows, report.columns, f"{tipo}.csv")

    if formato == "pdf":
        return Response(
            report.to_pdf(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={tipo}.pdf"}
        )

    return Response(
        report.to_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={tipo}.xlsx"}
    )


@router.post("/email/mora/{usuario_id}")
def send_mora(usuario_id: str, monto: float, user: dict = Depends(require_roles("admin", "tesorero"))):
    vecino = table("usuarios").select("email").eq("id", usuario_id).single().execute().data
    if not vecino:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    return EmailService().debt_alert(vecino["email"], monto)
