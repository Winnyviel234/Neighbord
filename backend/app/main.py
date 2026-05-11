from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.endpoints import auth as old_auth, comunicados, comunicados_publicos, cuotas, directiva, documentos, email_endpoints, finanzas, live, noticias, otros, reportes, reuniones, solicitudes, vecinos, votaciones
from app.modules.auth.routes import router as new_auth_router
from app.modules.users.routes import router as users_router
from app.modules.sectors.routes import router as sectors_router
from app.modules.roles.routes import router as roles_router
from app.modules.complaints.routes import router as complaints_router
from app.modules.chat.routes import router as chat_router
from app.modules.payments.routes import router as payments_router
from app.modules.meetings.routes import router as meetings_router
from app.modules.voting.routes import router as voting_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.statistics.routes import router as statistics_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include new modular routers
app.include_router(new_auth_router, prefix="/api/v2")
app.include_router(users_router, prefix="/api/v2")
app.include_router(sectors_router, prefix="/api/v2")
app.include_router(roles_router, prefix="/api/v2")
app.include_router(complaints_router, prefix="/api/v2")
app.include_router(chat_router, prefix="/api/v2")
app.include_router(payments_router, prefix="/api/v2")
app.include_router(meetings_router, prefix="/api/v2")
app.include_router(voting_router, prefix="/api/v2")
app.include_router(notifications_router, prefix="/api/v2")
app.include_router(statistics_router, prefix="/api/v2")

# Keep old routers for backward compatibility
app.include_router(old_auth.router, prefix="/api")
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
