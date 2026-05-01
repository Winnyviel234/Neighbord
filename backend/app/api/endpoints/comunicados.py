from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_roles
from app.core.supabase import table
from app.schemas.schemas import ComunicadoIn

router = APIRouter(prefix="/comunicados", tags=["comunicados"])


@router.get("")
def list_comunicados(user: dict = Depends(get_current_user)):
    return table("comunicados").select("*").order("created_at", desc=True).execute().data


@router.post("")
def create_comunicado(payload: ComunicadoIn, user: dict = Depends(require_roles("admin"))):
    data = payload.model_dump()
    data["autor_id"] = user["id"]
    return table("comunicados").insert(data).execute().data[0]


@router.patch("/{comunicado_id}")
def update_comunicado(comunicado_id: str, payload: ComunicadoIn, user: dict = Depends(require_roles("admin"))):
    return table("comunicados").update(payload.model_dump()).eq("id", comunicado_id).execute().data[0]


@router.delete("/{comunicado_id}")
def delete_comunicado(comunicado_id: str, user: dict = Depends(require_roles("admin"))):
    return table("comunicados").delete().eq("id", comunicado_id).execute().data[0]
