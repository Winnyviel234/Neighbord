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

    def select(self, columns: str = "*"):
        self.method = "GET"
        self.params["select"] = columns
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

    def order(self, column: str, desc: bool = False):
        self.params["order"] = f"{column}.{'desc' if desc else 'asc'}"
        return self

    def limit(self, value: int):
        self.params["limit"] = str(value)
        return self

    def single(self):
        self.headers["Accept"] = "application/vnd.pgrst.object+json"
        return self

    def execute(self) -> SupabaseResult:
        with httpx.Client(timeout=20) as client:
            response = client.request(
                self.method,
                self._url(),
                params=self.params,
                json=self.payload,
                headers=self._base_headers(),
            )
        if response.status_code >= 400:
            if response.status_code == 406 and self.headers.get("Accept"):
                return SupabaseResult(None)
            response.raise_for_status()
        if not response.content:
            if self.method == "DELETE":
                return SupabaseResult([{"deleted": True}])
            return SupabaseResult(None)
        data = response.json()
        if self.method == "DELETE" and data == []:
            return SupabaseResult([{"deleted": True}])
        return SupabaseResult(data)


def table(name: str):
    return SupabaseTable(name)


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
