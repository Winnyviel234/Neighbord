from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import get_current_user, require_roles
from app.core.supabase import table, upload_to_storage
from app.schemas.schemas import CuotaIn, PagoCuotaIn, PagoIn

router = APIRouter(prefix="/cuotas", tags=["cuotas"])


def _enrich_pagos(rows: list[dict]) -> list[dict]:
    for row in rows:
        cuota = table("cuotas").select("titulo,monto,fecha_vencimiento").eq("id", row.get("cuota_id")).single().execute().data
        vecino = table("usuarios").select("nombre,email").eq("id", row.get("vecino_id")).single().execute().data
        row["cuota"] = cuota or {}
        row["vecino"] = vecino or {}
    return rows


def _payment_data(
    cuota_id: str,
    vecino_id: str,
    monto: float,
    fecha_pago: date,
    metodo: str,
    referencia: str | None,
    registrado_por: str,
    comprobante: UploadFile | None = None,
) -> dict:
    cuota = table("cuotas").select("id,estado").eq("id", cuota_id).single().execute().data
    if not cuota:
        raise HTTPException(status_code=404, detail="Cuota no encontrada")
    if cuota.get("estado") != "activa":
        raise HTTPException(status_code=400, detail="La cuota no esta activa")
    data = {
        "cuota_id": cuota_id,
        "vecino_id": vecino_id,
        "monto": monto,
        "fecha_pago": fecha_pago.isoformat(),
        "metodo": metodo,
        "referencia": referencia,
        "registrado_por": registrado_por,
        "estado": "pendiente",
        "verificado_por": None,
        "verificado_at": None,
    }
    if comprobante:
        data["comprobante_url"] = upload_to_storage(comprobante, "comprobantes-pago")
    return data


@router.get("")
def list_cuotas(user: dict = Depends(require_roles("admin", "directiva", "tesorero", "vecino"))):
    return table("cuotas").select("*").order("fecha_vencimiento", desc=True).execute().data


@router.post("")
def create_cuota(payload: CuotaIn, user: dict = Depends(require_roles("admin", "tesorero"))):
    data = payload.model_dump(mode="json")
    data["creado_por"] = user["id"]
    return table("cuotas").insert(data).execute().data[0]


@router.patch("/{cuota_id}")
def update_cuota(cuota_id: str, payload: CuotaIn, user: dict = Depends(require_roles("admin", "tesorero"))):
    data = payload.model_dump(mode="json")
    return table("cuotas").update(data).eq("id", cuota_id).execute().data[0]


@router.delete("/{cuota_id}")
def delete_cuota(cuota_id: str, user: dict = Depends(require_roles("admin"))):
    return table("cuotas").delete().eq("id", cuota_id).execute().data[0]


@router.get("/pagos")
def list_pagos_cuotas(user: dict = Depends(require_roles("admin", "directiva", "tesorero"))):
    rows = table("pagos_cuotas").select("*").order("fecha_pago", desc=True).execute().data or []
    return _enrich_pagos(rows)


@router.get("/mis-pagos")
def list_mis_pagos(user: dict = Depends(get_current_user)):
    cuotas = table("cuotas").select("*").order("fecha_vencimiento", desc=True).execute().data
    pagos = table("pagos_cuotas").select("*").eq("vecino_id", user["id"]).order("fecha_pago", desc=True).execute().data
    return {"cuotas": cuotas, "pagos": pagos}


@router.post("/{cuota_id}/pagos")
def pagar_cuota(cuota_id: str, payload: PagoIn, user: dict = Depends(require_roles("admin", "tesorero"))):
    data = _payment_data(cuota_id, payload.vecino_id, payload.monto, payload.fecha_pago, payload.metodo, payload.referencia, user["id"])
    return table("pagos_cuotas").upsert(data, on_conflict="cuota_id,vecino_id").execute().data[0]


@router.post("/{cuota_id}/pagar")
def pagar_mi_cuota(cuota_id: str, payload: PagoCuotaIn, user: dict = Depends(get_current_user)):
    data = _payment_data(cuota_id, user["id"], payload.monto, payload.fecha_pago, payload.metodo, payload.referencia, user["id"])
    return table("pagos_cuotas").upsert(data, on_conflict="cuota_id,vecino_id").execute().data[0]


@router.post("/{cuota_id}/pagar/form")
def pagar_mi_cuota_form(
    cuota_id: str,
    monto: float = Form(...),
    fecha_pago: date = Form(...),
    metodo: str = Form("transferencia"),
    referencia: str = Form(None),
    comprobante: UploadFile | None = File(None),
    user: dict = Depends(get_current_user),
):
    data = _payment_data(cuota_id, user["id"], monto, fecha_pago, metodo, referencia, user["id"], comprobante)
    return table("pagos_cuotas").upsert(data, on_conflict="cuota_id,vecino_id").execute().data[0]


@router.patch("/pagos/{pago_id}/estado/{estado}")
def cambiar_estado_pago(pago_id: str, estado: str, user: dict = Depends(require_roles("admin", "tesorero"))):
    if estado not in {"pendiente", "verificado", "rechazado"}:
        raise HTTPException(status_code=400, detail="Estado de pago invalido")
    data = {"estado": estado}
    if estado == "verificado":
        data.update({"verificado_por": user["id"], "verificado_at": datetime.now(timezone.utc).isoformat()})
    return table("pagos_cuotas").update(data).eq("id", pago_id).execute().data[0]
