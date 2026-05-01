from fastapi import APIRouter, Depends

from app.core.security import require_roles
from app.schemas.schemas import EmailIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/personalizado")
def send_custom(payload: EmailIn, user: dict = Depends(require_roles("admin", "directiva"))):
    return EmailService().send(payload.destinatarios, payload.asunto, f"<p>{payload.mensaje}</p>", payload.mensaje)


@router.post("/prueba")
def test_email(payload: EmailIn, user: dict = Depends(require_roles("admin"))):
    return EmailService().send(payload.destinatarios, payload.asunto, f"<p>{payload.mensaje}</p>", payload.mensaje)

