from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_roles
from app.core.supabase import table
from app.schemas.schemas import PagoIn, TransaccionIn
from app.services.email_service import EmailService

router = APIRouter(prefix="/finanzas", tags=["finanzas"])


@router.get("/pagos")
def pagos(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("pagos").select("*, usuarios(nombre,email)").order("fecha_pago", desc=True).execute().data


@router.post("/pagos")
def create_pago(payload: PagoIn, user: dict = Depends(require_roles("admin", "tesorero"))):
    data = payload.model_dump(mode="json")
    data["registrado_por"] = user["id"]
    pago = table("pagos").insert(data).execute().data[0]
    vecino = table("usuarios").select("email,nombre").eq("id", payload.vecino_id).single().execute().data
    if vecino and vecino.get("email"):
        EmailService().payment_receipt(vecino["email"], payload.concepto, payload.monto)
    return pago


@router.post("/pagos/solicitud")
def create_pago_solicitud(payload: PagoIn, user: dict = Depends(get_current_user)):
    data = payload.model_dump(mode="json")
    data["registrado_por"] = user["id"]
    pago = table("pagos").insert(data).execute().data[0]
    vecino = table("usuarios").select("email,nombre").eq("id", payload.vecino_id).single().execute().data
    if vecino and vecino.get("email"):
        EmailService().payment_receipt(vecino["email"], payload.concepto, payload.monto)
    return pago


@router.patch("/pagos/{pago_id}")
def update_pago(pago_id: str, payload: PagoIn, user: dict = Depends(require_roles("admin"))):
    return table("pagos").update(payload.model_dump(mode="json")).eq("id", pago_id).execute().data[0]


@router.delete("/pagos/{pago_id}")
def delete_pago(pago_id: str, user: dict = Depends(require_roles("admin"))):
    return table("pagos").delete().eq("id", pago_id).execute().data[0]


@router.get("/transacciones")
def transacciones(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    return table("transacciones").select("*").order("fecha", desc=True).execute().data


@router.post("/transacciones")
def create_transaccion(payload: TransaccionIn, user: dict = Depends(require_roles("admin", "tesorero"))):
    data = payload.model_dump(mode="json")
    data["registrado_por"] = user["id"]
    return table("transacciones").insert(data).execute().data[0]


@router.patch("/transacciones/{transaccion_id}")
def update_transaccion(transaccion_id: str, payload: TransaccionIn, user: dict = Depends(require_roles("admin"))):
    return table("transacciones").update(payload.model_dump(mode="json")).eq("id", transaccion_id).execute().data[0]


@router.delete("/transacciones/{transaccion_id}")
def delete_transaccion(transaccion_id: str, user: dict = Depends(require_roles("admin"))):
    return table("transacciones").delete().eq("id", transaccion_id).execute().data[0]
