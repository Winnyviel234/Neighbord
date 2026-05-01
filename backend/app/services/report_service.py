from io import BytesIO, StringIO
import csv

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class BaseReport:
    title = "Reporte"
    columns: list[str] = []

    def __init__(self, rows: list[dict]):
        self.rows = rows

    def to_pdf(self) -> bytes:
        buffer = BytesIO()
        doc = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50
        doc.setFont("Helvetica-Bold", 15)
        doc.drawString(40, y, self.title)
        y -= 35
        doc.setFont("Helvetica", 9)
        for row in self.rows:
            line = " | ".join(str(row.get(col, ""))[:32] for col in self.columns)
            doc.drawString(40, y, line)
            y -= 18
            if y < 60:
                doc.showPage()
                y = height - 50
                doc.setFont("Helvetica", 9)
        doc.save()
        buffer.seek(0)
        return buffer.read()

    def to_csv(self) -> bytes:
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(self.rows)
        return output.getvalue().encode("utf-8-sig")


class VecinosReport(BaseReport):
    title = "Reporte de vecinos"
    columns = ["nombre", "email", "telefono", "direccion", "estado"]


class FinancieroReport(BaseReport):
    title = "Reporte financiero"
    columns = ["tipo", "categoria", "descripcion", "monto", "fecha"]


class SolicitudesReport(BaseReport):
    title = "Reporte de solicitudes"
    columns = ["titulo", "categoria", "prioridad", "estado", "created_at"]


class ActaReunionReport(BaseReport):
    title = "Acta de reuniones"
    columns = ["titulo", "fecha", "lugar", "estado"]


class CronogramaReport(BaseReport):
    title = "Cronograma comunitario"
    columns = ["titulo", "descripcion", "fecha", "estado"]


class ReportFactory:
    reports = {
        "vecinos": VecinosReport,
        "financiero": FinancieroReport,
        "solicitudes": SolicitudesReport,
        "actas": ActaReunionReport,
        "cronograma": CronogramaReport,
    }

    @classmethod
    def create(cls, report_type: str, rows: list[dict]) -> BaseReport:
        report_cls = cls.reports.get(report_type)
        if not report_cls:
            raise ValueError("Tipo de reporte no soportado")
        return report_cls(rows)

