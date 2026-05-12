from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4
from typing import Any
import re
from io import BytesIO

import httpx

from app.core.config import settings


def _compress_image(content: bytes, filename: str) -> tuple[bytes, str]:
    """Comprime y optimiza imágenes. Retorna (content_comprimido, nombre_con_extension)"""
    try:
        from PIL import Image
        
        # Detectar si es imagen
        try:
            img = Image.open(BytesIO(content))
        except:
            return content, filename
        
        # Redimensionar si es muy grande (máximo 1200px)
        max_size = 1200
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        
        # Guardar como JPEG comprimido
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        compressed_content = output.getvalue()
        
        # Cambiar extensión a .jpg
        base_name = Path(filename).stem
        return compressed_content, f"{base_name}.jpg"
    except:
        return content, filename


@dataclass
class SupabaseResult:
    data: Any
    count: int | None = None


@dataclass
class SupabaseTable:
    name: str
    method: str = "GET"
    payload: Any = None
    params: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    def _base_headers(self) -> dict[str, str]:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError("Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en backend/.env")
        return {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
            **self.headers,
        }

    def _url(self) -> str:
        return f"{settings.supabase_url.rstrip('/')}/rest/v1/{self.name}"

    def select(self, columns: str = "*", count: str | None = None):
        self.method = "GET"
        cleaned_columns = re.sub(r"\s+", " ", columns).strip()
        self.params["select"] = cleaned_columns
        if count:
            prefer = self.headers.get("Prefer") or "return=representation"
            if "count=" not in prefer:
                self.headers["Prefer"] = f"{prefer},count={count}"
        return self

    def insert(self, data: dict | list[dict]):
        self.method = "POST"
        self.payload = data
        return self

    def update(self, data: dict):
        self.method = "PATCH"
        self.payload = data
        return self

    def delete(self):
        self.method = "DELETE"
        return self

    def upsert(self, data: dict | list[dict], on_conflict: str | None = None):
        self.method = "POST"
        self.payload = data
        self.headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        if on_conflict:
            self.params["on_conflict"] = on_conflict
        return self

    def eq(self, column: str, value: Any):
        self.params[column] = f"eq.{value}"
        return self

    def gt(self, column: str, value: Any):
        self.params[column] = f"gt.{value}"
        return self

    def gte(self, column: str, value: Any):
        self.params[column] = f"gte.{value}"
        return self

    def lt(self, column: str, value: Any):
        self.params[column] = f"lt.{value}"
        return self

    def lte(self, column: str, value: Any):
        self.params[column] = f"lte.{value}"
        return self

    def or_(self, *conditions: str):
        existing = self.params.get("or")
        if existing:
            self.params["or"] = ",".join([existing, *conditions])
        else:
            self.params["or"] = ",".join(conditions)
        return self

    def in_(self, column: str, values: list[str] | tuple[str, ...]):
        formatted = ",".join(str(v) for v in values)
        self.params[column] = f"in.({formatted})"
        return self

    def order(self, column: str, desc: bool = False):
        self.params["order"] = f"{column}.{'desc' if desc else 'asc'}"
        return self

    def limit(self, value: int):
        self.params["limit"] = str(value)
        return self

    def single(self):
        self.headers["Accept"] = "application/vnd.pgrst.object+json"
        return self

    def _reset(self):
        self.method = "GET"
        self.payload = None
        self.params = {}
        self.headers = {}

    def execute(self) -> SupabaseResult:
        method = self.method
        headers = self._base_headers()
        accepts_single = bool(self.headers.get("Accept"))
        try:
            with httpx.Client(timeout=20) as client:
                response = client.request(
                    method,
                    self._url(),
                    params=dict(self.params),
                    json=self.payload,
                    headers=headers,
                )
            content_range = response.headers.get("content-range", "")
            total_count = None
            if "/" in content_range:
                try:
                    total_count = int(content_range.rsplit("/", 1)[1])
                except ValueError:
                    total_count = None
            if response.status_code >= 400:
                if response.status_code == 406 and accepts_single:
                    return SupabaseResult(None, count=0)
                if response.status_code == 404 and method == "GET":
                    # Missing table or view in Supabase can happen in dev; return safe fallback rather than crashing.
                    return SupabaseResult(None if accepts_single else [], count=0)
                response.raise_for_status()
            if not response.content:
                if method == "DELETE":
                    return SupabaseResult([{"deleted": True}], count=1)
                return SupabaseResult(None, count=total_count)
            data = response.json()
            if method == "DELETE" and data == []:
                return SupabaseResult([{"deleted": True}], count=1)
            return SupabaseResult(data, count=total_count)
        finally:
            self._reset()


def table(name: str):
    return SupabaseTable(name)


def execute_sql(sql: str):
    """Execute raw SQL on Supabase using the exec_sql RPC function."""
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en backend/.env")

    url = f"{settings.supabase_url.rstrip('/')}/rest/v1/rpc/exec_sql"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=20) as client:
        response = client.post(url, json={"sql": sql}, headers=headers)
    response.raise_for_status()
    return response.json()


def upload_to_storage(file, bucket: str = "neighborhood-images") -> str | None:
    original_name = Path(file.filename or "archivo").name
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "-", original_name).strip("-") or "archivo"
    filename = f"{uuid4().hex}-{safe_name}"
    content = file.file.read()
    
    # Comprimir imagen si es necesario
    if file.content_type and file.content_type.startswith('image/'):
        content, filename = _compress_image(content, filename)

    if not settings.supabase_url or not settings.supabase_service_role_key:
        return save_local_upload(content, filename, bucket)
    try:
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "apikey": settings.supabase_service_role_key,
            "Content-Type": "image/jpeg" if filename.endswith('.jpg') else (file.content_type or "application/octet-stream"),
            "x-upsert": "true"
        }
        storage_path = f"{bucket}/{filename}"
        url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{storage_path}"
        response = httpx.put(url, headers=headers, content=content)
        if response.status_code in (200, 201):
            public_url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{storage_path}"
            return public_url
    except Exception:
        pass
    return save_local_upload(content, filename, bucket)


def save_local_upload(content: bytes, filename: str, bucket: str) -> str:
    base_dir = Path(__file__).resolve().parents[2] / "uploads" / bucket
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / filename).write_bytes(content)
    return f"/uploads/{bucket}/{filename}"
