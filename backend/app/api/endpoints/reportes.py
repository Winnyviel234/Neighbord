from fastapi import APIRouter, Depends, HTTPException, Response

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


@router.get("/{tipo}.{formato}")
def download_report(tipo: str, formato: str, user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    if tipo not in TABLES or formato not in ["pdf", "csv", "xlsx"]:
        raise HTTPException(status_code=404, detail="Reporte no disponible")
    rows = table(TABLES[tipo]).select("*").execute().data
    report = ReportFactory.create(tipo, rows)
    if formato == "pdf":
        return Response(report.to_pdf(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={tipo}.pdf"})
    content = report.to_csv()
    return Response(content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={tipo}.csv"})


@router.post("/email/mora/{usuario_id}")
def send_mora(usuario_id: str, monto: float, user: dict = Depends(require_roles("admin", "tesorero"))):
    vecino = table("usuarios").select("email").eq("id", usuario_id).single().execute().data
    if not vecino:
        raise HTTPException(status_code=404, detail="Vecino no encontrado")
    return EmailService().debt_alert(vecino["email"], monto)

