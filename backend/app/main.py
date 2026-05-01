from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.endpoints import auth, comunicados, comunicados_publicos, cuotas, directiva, documentos, email_endpoints, finanzas, live, noticias, otros, reportes, reuniones, solicitudes, vecinos, votaciones
from app.core.config import settings

app = FastAPI(title=settings.app_name)
uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(vecinos.router, prefix="/api")
app.include_router(reuniones.router, prefix="/api")
app.include_router(votaciones.router, prefix="/api")
app.include_router(finanzas.router, prefix="/api")
app.include_router(cuotas.router, prefix="/api")
app.include_router(solicitudes.router, prefix="/api")
app.include_router(comunicados.router, prefix="/api")
app.include_router(comunicados_publicos.router, prefix="/api")
app.include_router(noticias.router, prefix="/api")
app.include_router(otros.router, prefix="/api")
app.include_router(directiva.router, prefix="/api")
app.include_router(reportes.router, prefix="/api")
app.include_router(documentos.router, prefix="/api")
app.include_router(email_endpoints.router, prefix="/api")
app.include_router(live.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
