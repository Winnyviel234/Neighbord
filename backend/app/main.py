import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

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
from app.modules.search.routes import router as search_router
from app.modules.monitoring.routes import router as monitoring_router
from app.modules.directiva.routes import router as directiva_router
from app.modules.projects.routes import router as projects_router
from app.modules.audit.routes import router as audit_router
from app.modules.webhooks.routes import router as webhook_router
from app.modules.public_api.routes import router as public_api_router
from app.modules.oauth.routes import router as oauth_router
from app.modules.banking.routes import router as banking_router
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
    allow_origin_regex=r"^https?://(\[::1\]|localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d{1,3}\.\d{1,3}):\d+$",
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
app.include_router(search_router, prefix="/api/v2")
app.include_router(monitoring_router, prefix="/api/v2")
app.include_router(directiva_router, prefix="/api/v2")
app.include_router(projects_router, prefix="/api/v2")
app.include_router(audit_router, prefix="/api/v2")
app.include_router(webhook_router, prefix="/api/v2")
app.include_router(public_api_router, prefix="/api/v2")
app.include_router(oauth_router, prefix="/api/v2/auth")
app.include_router(banking_router, prefix="/api/v2")

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
