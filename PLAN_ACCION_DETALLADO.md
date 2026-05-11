# 🛠️ PLAN DE ACCIÓN PROFESIONAL - NEIGHBORD v2.1

**Objetivo:** Convertir el sistema actual en producción segura y escalable

**Timeline:** 4 semanas de trabajo enfocado

**Responsable:** Backend Lead + Frontend Lead + QA

---

## 📅 CRONOGRAMA DETALLADO

### FASE 1: FIXES CRÍTICOS DE SEGURIDAD (Semana 1 - 40 horas)

#### Sprint 1A: Vulnerabilidades Bloqueantes (Días 1-2)

**Tarea 1.1: JWT Secret Management** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 30 min
- **Archivos a modificar:**
  1. `backend/app/core/config.py`
  2. `.env` y `.env.example`
  3. CI/CD secrets

**Código (backend/app/core/config.py):**
```python
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Neighbord Community System"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    # 🔒 JWT SECURITY: Usar variable de entorno fuerte
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "DEBE_SER_REEMPLAZADO_EN_.ENV"  # Comentario que aparece en dev
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validación en runtime
        if self.environment == "production" and self.jwt_secret_key == "DEBE_SER_REEMPLAZADO_EN_.ENV":
            raise ValueError("⚠️ JWT_SECRET_KEY no está configurada en producción")
        if len(self.jwt_secret_key) < 32 and self.environment == "production":
            raise ValueError("⚠️ JWT_SECRET_KEY es muy débil (mínimo 32 caracteres)")

    # ... resto de configuración
```

**Archivo `.env.example`:**
```bash
# 🔒 SECURITY - JWT Secret (Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=generate-strong-32-char-key-here-or-use-python-command

# ... resto de config
```

**Script para generar key segura** (`backend/scripts/generate_jwt_secret.py`):
```python
#!/usr/bin/env python3
import secrets

secret = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={secret}")
print(f"\n✅ Copiar esta línea en .env")
```

---

**Tarea 1.2: Proteger Endpoints Públicos** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 1 hora
- **Archivos afectados:** 5

**1. Voting - GET / (backend/app/modules/voting/routes.py - Línea 14)**

```python
# ❌ ANTES
@router.get("/")
async def get_votaciones(limit: int = 100):
    """List all votaciones"""
    return await voting_service.list_votaciones(limit)

# ✅ DESPUÉS
@router.get("/")
async def get_votaciones(
    limit: int = 100,
    user: dict = Depends(get_current_user)  # 🔒 ADD THIS LINE
):
    """List all votaciones (requires authentication)"""
    return await voting_service.list_votaciones(limit, user["sector_id"])
```

**2. Meetings - GET / y GET /{id} (backend/app/modules/meetings/routes.py)**

```python
# ❌ ANTES (Línea 11)
@router.get("/")
async def list_meetings(limit: int = 100):
    return await meetings_service.list_meetings(limit)

# ✅ DESPUÉS
@router.get("/")
async def list_meetings(
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    return await meetings_service.list_meetings(limit, user["sector_id"])

# ❌ ANTES (Línea 53)
@router.get("/{meeting_id}")
async def get_meeting(meeting_id: UUID):
    return await meetings_service.get_meeting(meeting_id)

# ✅ DESPUÉS
@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: UUID,
    user: dict = Depends(get_current_user)
):
    meeting = await meetings_service.get_meeting(meeting_id)
    # Validar que el usuario pertenece al sector
    if meeting["sector_id"] != user["sector_id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta reunión")
    return meeting
```

**3. Sectors - GET / y GET /{id} (backend/app/modules/sectors/routes.py)**

```python
# ❌ ANTES
@router.get("/")
async def list_sectors():
    return await sectors_service.list_sectors()

# ✅ DESPUÉS
@router.get("/")
async def list_sectors(user: dict = Depends(get_current_user)):
    # Solo mostrar el sector del usuario (multi-tenancy)
    return await sectors_service.get_sector(user["sector_id"])

# NOTA: Mantener GET / admin para listar todos (con permisos)
@router.get("/admin/all")
async def list_all_sectors(user: dict = Depends(require_permissions(["manage_sectors"]))):
    return await sectors_service.list_sectors()
```

**4. Payments - GET /fees (backend/app/modules/payments/routes.py - Línea 44)**

```python
# ❌ ANTES
@router.get("/fees")
async def get_fees():
    """Get all community fees"""
    return await payments_service.get_fees()

# ✅ DESPUÉS
@router.get("/fees")
async def get_fees(user: dict = Depends(get_current_user)):
    """Get community fees (requires authentication)"""
    return await payments_service.get_fees(user["sector_id"])
```

**5. Live - WebSocket (backend/app/api/endpoints/live.py)**

```python
# ❌ ANTES (Sin autenticación)
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # ... sin validación

# ✅ DESPUÉS (Con JWT validation)
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    try:
        # Obtener token del query string
        query_params = parse.parse_qs(websocket.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        
        if not token:
            await websocket.close(code=1008, reason="Token requerido")
            return
        
        # Validar JWT
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("sub")
        except JWTError:
            await websocket.close(code=1008, reason="Token inválido")
            return
        
        await websocket.accept()
        # ... resto del código
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
```

---

**Tarea 1.3: Proteger WebSocket Chat** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 1 hora
- **Archivo:** `backend/app/modules/chat/routes.py`

```python
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from jose import jwt, JWTError
from urllib.parse import parse_qs

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """
    WebSocket endpoint para chat en tiempo real.
    REQUERIDO: Token JWT en query string ?token=xxx
    """
    try:
        # 1. Extraer y validar token
        query_params = parse_qs(websocket.scope.get("query_string", b"").decode())
        token_list = query_params.get("token", [])
        
        if not token_list:
            await websocket.close(code=1008, reason="Token requerido")
            return
        
        token = token_list[0]
        
        # 2. Decodificar JWT
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=1008, reason="Token inválido")
                return
        except JWTError:
            await websocket.close(code=1008, reason="Token expirado o inválido")
            return
        
        # 3. Obtener usuario y sector
        user = await auth_service.get_user_by_id(user_id)
        if not user or not user.get("activo"):
            await websocket.close(code=1008, reason="Usuario inactivo")
            return
        
        # 4. Validar acceso al room (por sector)
        room = await chat_service.get_room(room_id)
        if not room or room["sector_id"] != user["sector_id"]:
            await websocket.close(code=1008, reason="No tienes acceso a esta sala")
            return
        
        # 5. Conexión exitosa
        await websocket.accept()
        await chat_service.connect(room_id, user_id, websocket)
        
        # 6. Escuchar mensajes
        try:
            while True:
                data = await websocket.receive_text()
                
                # Sanitizar entrada
                message = sanitize_html(data.strip())
                if not message or len(message) > 5000:
                    continue
                
                # Guardar y broadcast
                await chat_service.save_message(room_id, user_id, message)
                await chat_service.broadcast(room_id, {
                    "type": "message",
                    "user_id": str(user_id),
                    "user_name": user["nombre"],
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
        except WebSocketDisconnect:
            await chat_service.disconnect(room_id, user_id)
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011)
```

---

**Tarea 1.4: Agregar Constraints a BD** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 30 min
- **Archivo:** `backend/migration_phase9_security.sql` (nuevo)

```sql
-- ============================================================
-- 🔒 SECURITY CONSTRAINTS - Phase 9 Migration
-- ============================================================
-- Prevenir voto múltiple

ALTER TABLE votos DROP CONSTRAINT IF EXISTS unique_voting_per_user;
ALTER TABLE votos ADD CONSTRAINT unique_voting_per_user 
  UNIQUE(votacion_id, usuario_id);

-- Prevenir documento duplicado
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS unique_document;
ALTER TABLE usuarios ADD CONSTRAINT unique_document 
  UNIQUE(documento) WHERE documento IS NOT NULL;

-- Validación de email case-insensitive
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS unique_email_lower;
ALTER TABLE usuarios ADD CONSTRAINT unique_email_lower 
  UNIQUE(LOWER(email));

-- Índices para performance en queries comunes
CREATE INDEX IF NOT EXISTS idx_votos_votacion_user 
  ON votos(votacion_id, usuario_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_date 
  ON audit_logs(usuario_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_room_date 
  ON messages(room_id, created_at DESC);

-- Trigger para auditoría automática
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (usuario_id, accion, tabla, registro_id, cambios_antes, cambios_despues, ip_address, user_agent)
  VALUES (
    current_user_id(),
    TG_OP,
    TG_TABLE_NAME,
    NEW.id,
    to_jsonb(OLD),
    to_jsonb(NEW),
    current_setting('app.client_ip', true),
    current_setting('app.user_agent', true)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a tablas críticas
DROP TRIGGER IF EXISTS audit_usuarios ON usuarios;
CREATE TRIGGER audit_usuarios AFTER INSERT OR UPDATE OR DELETE ON usuarios
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();

DROP TRIGGER IF EXISTS audit_votos ON votos;
CREATE TRIGGER audit_votos AFTER INSERT OR UPDATE OR DELETE ON votos
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();

DROP TRIGGER IF EXISTS audit_pagos_cuotas ON pagos_cuotas;
CREATE TRIGGER audit_pagos_cuotas AFTER INSERT OR UPDATE OR DELETE ON pagos_cuotas
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

**Script para ejecutar migración** (`backend/run_security_migration.py`):
```python
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

migration_file = Path(__file__).parent / "migration_phase9_security.sql"

try:
    # Conectar a Supabase y ejecutar SQL
    from app.core.supabase import supabase
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    # Ejecutar en bloques para mejor control de errores
    for statement in sql.split(';'):
        if statement.strip():
            result = supabase.rpc('execute_sql', {'sql': statement}).execute()
            print(f"✅ Ejecutado: {statement[:50]}...")
    
    print("✅ Migración de seguridad completada exitosamente")
except Exception as e:
    print(f"❌ Error en migración: {str(e)}")
    sys.exit(1)
```

---

**Tarea 1.5: Sanitización de entrada** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 1 hora
- **Archivo:** `backend/app/core/sanitization.py` (nuevo)

```python
import re
from html import escape
from typing import Any

class InputSanitizer:
    """Sanitizar entradas para prevenir XSS e inyección"""
    
    # Patrones peligrosos
    DANGEROUS_TAGS = re.compile(r'<script|<iframe|<object|<embed|javascript:|on\w+\s*=', re.IGNORECASE)
    SQL_INJECTION_PATTERN = re.compile(r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)", re.IGNORECASE)
    
    @staticmethod
    def sanitize_html(text: str, max_length: int = 5000) -> str:
        """
        Sanitizar HTML/texto para prevenir XSS
        - Escapar caracteres peligrosos
        - Limitar longitud
        - Remover scripts
        """
        if not isinstance(text, str):
            return ""
        
        # Limitar longitud
        text = text[:max_length]
        
        # Detectar y remover patrones peligrosos
        if InputSanitizer.DANGEROUS_TAGS.search(text):
            raise ValueError("Contenido con etiquetas peligrosas detectado")
        
        # Escapar caracteres HTML
        text = escape(text)
        
        return text
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_documento(documento: str, tipo: str = "cedula") -> bool:
        """Validar formato de documento por tipo"""
        patterns = {
            "cedula": r'^\d{10}$',  # 10 dígitos
            "pasaporte": r'^[A-Z]{2}\d{6,8}$',  # Formato pasaporte
            "nit": r'^\d{10,13}$',
        }
        pattern = patterns.get(tipo, patterns["cedula"])
        return bool(re.match(pattern, documento))

# Uso en modelos Pydantic
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    nombre: str
    email: str
    documento: str
    documento_tipo: str = "cedula"
    
    @validator('nombre')
    def sanitize_nombre(cls, v):
        return InputSanitizer.sanitize_html(v, max_length=100)
    
    @validator('email')
    def validate_email_format(cls, v):
        if not InputSanitizer.validate_email(v):
            raise ValueError("Email inválido")
        return v.lower()
    
    @validator('documento')
    def validate_documento_format(cls, v):
        if not InputSanitizer.validate_documento(v):
            raise ValueError("Formato de documento inválido")
        return v
```

---

#### Sprint 1B: Security Middleware (Días 3-4)

**Tarea 1.6: Rate Limiting** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 1.5 horas
- **Archivo:** `backend/app/core/middleware.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

def setup_rate_limiting(app: FastAPI):
    """Configurar rate limiting por endpoint"""
    
    # Auth endpoints - más restrictivos
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return app

async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
    )

# En app/modules/auth/routes.py:
from slowapi import limiter

@router.post("/login")
@limiter.limit("5/minute")  # 5 intentos por minuto
async def login(request: Request, payload: LoginRequest):
    return await auth_service.login(payload)

@router.post("/register")
@limiter.limit("3/minute")  # 3 registros por minuto
async def register(request: Request, payload: RegisterRequest):
    return await auth_service.register(payload)

@router.post("/change-password")
@limiter.limit("3/hour")
async def change_password(request: Request, payload: PasswordChangeRequest, user: dict = Depends(get_current_user)):
    return await auth_service.change_password(user["id"], payload)
```

---

**Tarea 1.7: Security Headers** ✅
- **Prioridad:** 🔴 CRÍTICO
- **Tiempo:** 30 min
- **Archivo:** `backend/app/core/middleware.py` (agregar)

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar security headers HTTP"""
    
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        
        # HSTS - Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP - Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.supabase.co; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options - Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection - Legacy XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        return response

# En app/main.py, después de crear la app:
app.add_middleware(SecurityHeadersMiddleware)
```

---

#### Sprint 1C: Validación de Entrada (Día 5)

**Tarea 1.8: Pydantic Validators en todos los modelos** ✅
- **Prioridad:** 🟡 ALTO
- **Tiempo:** 2 horas
- **Archivos:** Todos los `*/model.py`

**Ejemplo (backend/app/modules/voting/model.py):**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.core.sanitization import InputSanitizer

class VotingCreate(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field(..., max_length=2000)
    opciones: List[str] = Field(..., min_items=2, max_items=10)
    fecha_fin: datetime
    
    @validator('titulo')
    def sanitize_titulo(cls, v):
        return InputSanitizer.sanitize_html(v, max_length=200)
    
    @validator('descripcion')
    def sanitize_descripcion(cls, v):
        return InputSanitizer.sanitize_html(v, max_length=2000)
    
    @validator('opciones', pre=True)
    def validate_opciones(cls, v):
        if not isinstance(v, list):
            raise ValueError("opciones debe ser una lista")
        
        opciones_sanitizadas = []
        for opcion in v:
            if not isinstance(opcion, str):
                raise ValueError("Cada opción debe ser texto")
            sanitizada = InputSanitizer.sanitize_html(opcion, max_length=100)
            if sanitizada in opciones_sanitizadas:
                raise ValueError("Opciones duplicadas no permitidas")
            opciones_sanitizadas.append(sanitizada)
        
        return opciones_sanitizadas
    
    @validator('fecha_fin')
    def validate_fecha_fin(cls, v):
        if v <= datetime.now():
            raise ValueError("La fecha de fin debe ser en el futuro")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "¿Pintar la fachada del edificio?",
                "descripcion": "Votación para decidir si pintamos la fachada",
                "opciones": ["Sí", "No", "Postergar"],
                "fecha_fin": "2024-12-31T23:59:59"
            }
        }
```

---

### FASE 2: MÓDULOS INCOMPLETOS (Semana 2 - 40 horas)

#### Tarea 2.1: Mapa de Incidencias
- **Prioridad:** 🔴 CRÍTICO (requerimiento)
- **Tiempo:** 3 horas
- **Archivos:** Backend + Frontend

**Backend (backend/app/modules/search/routes.py - agregar):**
```python
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from uuid import UUID
from app.core.security import get_current_user

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/incidents/map")
async def get_incidents_map(
    sector_id: UUID = None,
    tipo: str = Query(None, enum=["queja", "proyecto", "evento"]),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    days_back: int = Query(30, ge=1, le=365),
    user: dict = Depends(get_current_user)
):
    """
    Obtener incidencias geolocalizadas para mostrar en mapa
    - Quejas (solicitudes) con ubicación
    - Proyectos comunitarios
    - Eventos/Reuniones
    """
    sector_id = sector_id or user["sector_id"]
    
    # Validar acceso al sector
    if sector_id != user["sector_id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este sector")
    
    desde = datetime.now() - timedelta(days=days_back)
    
    # Obtener quejas con ubicación
    complaints = await get_incidents_by_type(
        "solicitudes",
        sector_id,
        desde,
        tipo="queja" if tipo is None or tipo == "queja" else None
    )
    
    # Obtener proyectos con ubicación
    projects = await get_incidents_by_type(
        "proyectos",
        sector_id,
        desde,
        tipo="proyecto" if tipo is None or tipo == "proyecto" else None
    )
    
    # Obtener reuniones con ubicación
    meetings = await get_incidents_by_type(
        "reuniones",
        sector_id,
        desde,
        tipo="evento" if tipo is None or tipo == "evento" else None
    )
    
    return {
        "incidents": complaints + projects + meetings,
        "count": len(complaints) + len(projects) + len(meetings),
        "sector_id": str(sector_id),
        "timestamp": datetime.now().isoformat()
    }

async def get_incidents_by_type(table, sector_id, desde, tipo=None):
    """Helper para obtener incidencias de una tabla"""
    result = await table_client(table).select("""
        id, titulo, descripcion, estado, 
        lat, lng, created_at, categoria
    """).eq("sector_id", sector_id).gte("created_at", desde.isoformat()).execute()
    
    return [{
        "id": str(r["id"]),
        "title": r.get("titulo"),
        "description": r.get("descripcion"),
        "status": r.get("estado"),
        "type": tipo or "incident",
        "lat": float(r["lat"]),
        "lng": float(r["lng"]),
        "date": r["created_at"],
        "category": r.get("categoria")
    } for r in result.data if r.get("lat") and r.get("lng")]
```

---

#### Tarea 2.2: WhatsApp Integration Completa
- **Prioridad:** 🟡 ALTO (requerimiento)
- **Tiempo:** 2 horas
- **Archivo:** `backend/app/services/notification_service.py`

```python
def send_whatsapp(phone: str, message: str, template_vars: dict = None) -> bool:
    """
    Enviar mensaje por WhatsApp via Twilio
    phone: número en formato internacional (+56912345678)
    """
    if not settings.whatsapp_enabled:
        logger.warning(f"WhatsApp deshabilitado, mensaje no enviado a {phone}")
        return False
    
    try:
        from twilio.rest import Client
        
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        # Usar template de Twilio si es disponible
        if template_vars:
            # Reemplazar variables
            for key, value in template_vars.items():
                message = message.replace(f"{{{{{key}}}}}", str(value))
        
        message_obj = client.messages.create(
            from_=f"whatsapp:{settings.twilio_from_number}",
            to=f"whatsapp:{phone}",
            body=message
        )
        
        logger.info(f"WhatsApp enviado exitosamente: {message_obj.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando WhatsApp: {str(e)}")
        return False

# Integración en notificaciones
async def notify_payment_status(pago_id: UUID, status: str) -> dict:
    """Notificar cambio de estado de pago"""
    pago = await get_pago(pago_id)
    usuario = await get_usuario(pago["vecino_id"])
    
    # Email
    send_email_payment_status(usuario, pago, status)
    
    # WhatsApp
    if usuario.get("telefono"):
        mensajes = {
            "verificado": f"✅ Tu pago de ${pago['monto']} fue verificado. Ref: {pago['id']}",
            "rechazado": f"❌ Tu pago de ${pago['monto']} fue rechazado. Contacta a tesorero.",
            "pendiente": f"⏳ Tu pago de ${pago['monto']} está pendiente de verificación."
        }
        send_whatsapp(usuario["telefono"], mensajes.get(status, "Estado de pago actualizado"))
    
    return {"email_sent": True, "whatsapp_sent": True}
```

---

#### Tarea 2.3: Dashboard de Auditoría
- **Prioridad:** 🟡 ALTO
- **Tiempo:** 2 horas
- **Archivo:** Frontend - nueva página

```jsx
// frontend/src/pages/AuditDashboardPage.jsx
import React, { useState, useEffect } from 'react';
import { BarChart, LineChart, PieChart } from 'recharts';
import { AlertCircle, TrendingUp, Users, AlertTriangle } from 'lucide-react';

export default function AuditDashboardPage() {
  const [auditSummary, setAuditSummary] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ start: new Date(Date.now() - 30*24*60*60*1000), end: new Date() });

  useEffect(() => {
    fetchAuditData();
  }, [dateRange]);

  const fetchAuditData = async () => {
    try {
      const response = await dataService.getAuditLogs({
        start_date: dateRange.start,
        end_date: dateRange.end,
        limit: 1000
      });
      setAuditLogs(response);

      // Procesar para gráficos
      const summary = processAuditSummary(response);
      setAuditSummary(summary);
    } catch (error) {
      console.error('Error loading audit data:', error);
    } finally {
      setLoading(false);
    }
  };

  const processAuditSummary = (logs) => {
    const actions = {};
    const users = {};
    const tables = {};

    logs.forEach(log => {
      actions[log.action] = (actions[log.action] || 0) + 1;
      users[log.usuario_id] = (users[log.usuario_id] || 0) + 1;
      tables[log.tabla] = (tables[log.tabla] || 0) + 1;
    });

    return {
      totalActions: logs.length,
      actionsByType: Object.entries(actions).map(([name, value]) => ({ name, value })),
      topUsers: Object.entries(users).slice(0, 5).map(([id, count]) => ({ id, count })),
      tableChanges: Object.entries(tables).map(([name, count]) => ({ name, count }))
    };
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Dashboard de Auditoría</h1>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-500">Total Acciones</p>
              <p className="text-2xl font-bold">{auditSummary?.totalActions || 0}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-500">Usuarios Activos</p>
              <p className="text-2xl font-bold">{auditSummary?.topUsers?.length || 0}</p>
            </div>
            <Users className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-500">Tablas Modificadas</p>
              <p className="text-2xl font-bold">{auditSummary?.tableChanges?.length || 0}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-500">Alertas</p>
              <p className="text-2xl font-bold">3</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-bold mb-4">Acciones por Tipo</h3>
          <BarChart width={400} height={300} data={auditSummary?.actionsByType || []}>
            {/* Componentes Recharts */}
          </BarChart>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-bold mb-4">Cambios por Tabla</h3>
          <PieChart width={400} height={300} data={auditSummary?.tableChanges || []}>
            {/* Componentes Recharts */}
          </PieChart>
        </div>
      </div>

      {/* Logs Recientes */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-bold mb-4">Logs Recientes</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Usuario</th>
              <th className="text-left p-2">Acción</th>
              <th className="text-left p-2">Tabla</th>
              <th className="text-left p-2">Fecha</th>
              <th className="text-left p-2">IP</th>
            </tr>
          </thead>
          <tbody>
            {auditLogs.slice(0, 20).map(log => (
              <tr key={log.id} className="border-b hover:bg-gray-50">
                <td className="p-2">{log.usuario_nombre}</td>
                <td className="p-2">{log.accion}</td>
                <td className="p-2">{log.tabla}</td>
                <td className="p-2">{new Date(log.created_at).toLocaleString()}</td>
                <td className="p-2 font-mono text-xs">{log.ip_address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

### FASE 3: DOCUMENTACIÓN (Semana 3-4 - 40 horas)

#### Tarea 3.1: Mejorar README.md
**Ver sección siguiente: MEJORA DEL README**

#### Tarea 3.2: Manual de Usuario por Rol
- **Prioridad:** 🟡 ALTO
- **Archivos:** `docs/MANUAL_USUARIO_ADMIN.md`, `docs/MANUAL_USUARIO_VECINO.md`, etc.

#### Tarea 3.3: API Documentation
- **Prioridad:** 🟡 ALTO
- **Herramienta:** FastAPI OpenAPI (automático en `/docs`)

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

```markdown
### FASE 1 - Seguridad (Semana 1)
- [ ] JWT Secret en .env
- [ ] Proteger endpoints públicos
- [ ] WebSocket auth
- [ ] SQL constraints
- [ ] Sanitización
- [ ] Rate limiting
- [ ] Security headers
- [ ] Pydantic validators

### FASE 2 - Completar Módulos (Semana 2)
- [ ] Mapa de incidencias backend
- [ ] Mapa de incidencias frontend
- [ ] WhatsApp integration
- [ ] Dashboard auditoría
- [ ] Reporte anual

### FASE 3 - Documentación (Semana 3)
- [ ] README mejorado
- [ ] Manual usuario admin
- [ ] Manual usuario vecino
- [ ] API docs actualizadas
- [ ] Manual técnico

### FASE 4 - Testing y Deploy (Semana 4)
- [ ] Tests de seguridad
- [ ] Tests de funcionalidad
- [ ] Load testing
- [ ] Penetration testing
- [ ] Deploy staging
- [ ] Checklist producción
```

---

**Documento:** PLAN_ACCION_DETALLADO.md
**Versión:** 1.0
**Última actualización:** May 5, 2026
**Estado:** 🟢 LISTO PARA IMPLEMENTACIÓN
