# Resumen Ejecutivo - Vulnerabilidades Críticas del Backend

**Criticidad:** 🔴 **CRÍTICA - ACCIÓN INMEDIATA REQUERIDA**

---

## Quick Facts

| Métrica | Valor |
|---------|-------|
| **Módulos Implementados** | 21 (moderno) + 16 (legacy) |
| **Total de Endpoints** | ~150+ |
| **Vulnerabilidades Críticas** | 🔴 12 |
| **Vulnerabilidades Altas** | 🟡 8 |
| **Endpoints Públicos Sin Protección** | 🔴 6+ |
| **WebSockets Sin Autenticación** | 🔴 2 |
| **Rate Limiting Implementado** | ❌ NO |

---

## 🔴 TOP 5 Vulnerabilidades Críticas (Fix TODAY)

### 1. VOTING - Enumeración + Voto Múltiple + Privilege Escalation
**Archivo:** `/app/modules/voting/routes.py` (línea 15)  
**Problema:**
```python
@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None)
):  # ← SIN AUTENTICACIÓN
```

**Impacto:** 
- 🔴 Enumeración de votaciones
- 🔴 Voto múltiple permitido
- 🔴 Asignación de roles arbitraria

**Fix de 2 líneas:**
```python
@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)  # ← AGREGAR
):
```

---

### 2. WEBSOCKET LIVE - Completamente Sin Autenticación
**Archivo:** `/app/api/endpoints/live.py` (línea ~80)  
**Problema:**
```python
@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()  # ← TODOS TIENEN ACCESO
```

**Impacto:**
- 🔴 Acceso sin credenciales
- 🔴 XSS potencial
- 🔴 DDoS fácil

**Fix Temporal (bloquear en prod):**
```python
# Comentar endpoint o retornar 403
```

---

### 3. SECTORS - Enumeración de Estructura Organizacional
**Archivo:** `/app/modules/sectors/routes.py` (línea 9-11)  
**Problema:**
```python
@router.get("", response_model=List[SectorResponse])
async def get_sectors():  # ← PÚBLICO
```

**Impacto:**
- 🔴 Expone estructura organizacional
- 🔴 Información de divisiones

**Fix:**
```python
@router.get("", response_model=List[SectorResponse])
async def get_sectors(user: dict = Depends(get_current_user)):  # ← AGREGAR
```

---

### 4. MEETINGS - Listado Público + Asistencia Expuesta
**Archivo:** `/app/modules/meetings/routes.py` (línea 11-18, 53-56)  
**Problema:**
```python
@router.get("")
async def get_meetings(...):  # ← SIN AUTH

@router.get("/{meeting_id}/attendances")
async def get_attendances(meeting_id: UUID):  # ← SIN AUTH
```

**Impacto:**
- 🔴 Lista de reuniones pública
- 🔴 Asistencia de personas conocida

**Fix:** Agregar `user: dict = Depends(get_current_user)` en ambos

---

### 5. SQL INJECTION - votaciones.py _parse_election_option()
**Archivo:** `/app/api/endpoints/votaciones.py` (línea 8-14)  
**Problema:**
```python
def _parse_election_option(option: str) -> dict[str, str]:
    parts = option.split("|")  # ← Sin validación
    if not parts or parts[0] != "election":
        return {}
    values = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")  # ← Injection aquí
        values[key] = value  # ← Se guarda directamente
    return values
```

**Impacto:**
- 🔴 Inyección de campos arbitrarios
- 🔴 Asignación de roles fraudulenta

**Fix:** Whitelist de campos permitidos
```python
ALLOWED_FIELDS = {"user", "role"}
for part in parts[1:]:
    key, _, value = part.partition("=")
    if key in ALLOWED_FIELDS:  # ← VALIDAR
        values[key] = value
```

---

## 🟡 Vulnerabilidades Altas (Fix This Week)

### A1. JWT Secret Débil
**Archivo:** `/app/core/config.py` (línea 15)
```python
jwt_secret_key: str = "cambia-esta-clave"  # 🔴 CAMBIAR
```
**Fix:** Usar env var
```python
jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "cambia-esta-clave")
```

### A2. Sin Rate Limiting Global
**Archivo:** `/app/main.py`  
**Fix:** Agregar middleware
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### A3. Sin Security Headers
**Archivo:** `/app/main.py`  
**Fix:**
```python
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### A4. Validación Débil de Password
**Archivo:** `/app/modules/auth/model.py`  
**Fix:**
```python
from pydantic import field_validator
import re

class RegisterRequest(BaseModel):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be 8+ chars')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Need uppercase')
        if not re.search(r'[0-9]', v):
            raise ValueError('Need number')
        return v
```

### A5. GET /fees Sin Protección
**Archivo:** `/app/modules/payments/routes.py` (línea 44)
```python
@router.get("/fees")
async def get_fees():  # ← AGREGAR PROTECCIÓN
    return await payment_service.get_fees()
```

### A6. CORS Demasiado Permisivo
**Archivo:** `/app/main.py` (línea 25-31)
```python
allow_methods=["*"],  # ⚠️ CAMBIAR A ["GET", "POST", "PUT", "PATCH", "DELETE"]
allow_headers=["*"],  # ⚠️ CAMBIAR A ["Content-Type", "Authorization"]
```

### A7. Sin Validación en Payments
**Archivo:** `/app/modules/payments/model.py`  
**Problema:** Monto sin validación
```python
class PaymentCreate(BaseModel):
    monto: float  # ⚠️ SIN VALIDACIÓN
```
**Fix:**
```python
from pydantic import field_validator

class PaymentCreate(BaseModel):
    monto: float
    
    @field_validator('monto')
    def validate_monto(cls, v):
        if v <= 0:
            raise ValueError('Monto debe ser positivo')
        if v > 1000000:
            raise ValueError('Monto muy alto')
        return round(v, 2)
```

### A8. Chat Messages Sin Sanitización
**Archivo:** `/app/modules/chat/routes.py`  
**Fix:** Usar bleach o similar
```python
import bleach

message = await chat_service.send_message(room_id, payload, user)
# Sanitizar
payload.content = bleach.clean(payload.content, strip=True)
```

---

## Tabla de Prioridades

### NIVEL 1: HACER HOY (2-3 horas)
```
1. Proteger GET /voting (módulos/voting/routes.py:15)
2. Proteger GET /meetings (módulos/meetings/routes.py:11)
3. Proteger GET /sectors (módulos/sectors/routes.py:9)
4. Proteger GET /fees (módulos/payments/routes.py:44)
5. Comentar WebSocket /live (endpoints/live.py)
6. Cambiar JWT_SECRET_KEY
```

### NIVEL 2: ESTA SEMANA (1-2 días)
```
7. Implementar rate limiting
8. Agregar security headers
9. Validadores de password
10. Validadores de monto
11. Fix SQL injection en votaciones.py
12. Sanitización de chat messages
```

### NIVEL 3: PRÓXIMA SEMANA
```
13. Migrar endpoints legacy
14. Eliminar duplicación
15. Implementar tests
```

---

## Scripts de Remediación Rápida

### Script 1: Agregar Autenticación a 4 Endpoints
```bash
# Cambios necesarios:

# 1. voting/routes.py línea 15:
# Agregar: user: dict = Depends(get_current_user)

# 2. meetings/routes.py línea 11:
# Agregar: user: dict = Depends(get_current_user)

# 3. sectors/routes.py línea 9:
# Agregar: user: dict = Depends(get_current_user)

# 4. payments/routes.py línea 44:
# Agregar: user: dict = Depends(get_current_user)
```

### Script 2: Cambiar JWT Secret
```bash
# .env
JWT_SECRET_KEY=tu-secret-aleatorio-fuerte-de-64-caracteres
```

### Script 3: Deshabilitar WebSocket Live
```python
# Comentar en main.py
# app.include_router(live.router, prefix="/api")
```

---

## Verificación Post-Fix

Después de aplicar fixes, verificar:

```bash
# 1. ¿Endpoints públicos ahora requieren auth?
curl http://localhost:8000/api/v2/voting/
# Debe retornar 401

# 2. ¿JWT secret cambió?
grep "cambia-esta-clave" backend/app/core/config.py
# Debe estar vacío

# 3. ¿Rate limiting activo?
for i in {1..100}; do curl http://localhost:8000/api/health; done
# Debe fallar después de N requests

# 4. ¿Security headers presentes?
curl -i http://localhost:8000/api/health | grep X-Frame-Options
# Debe mostrar: X-Frame-Options: DENY
```

---

## Contactos y Escalación

**Personas a Notificar:**
- [ ] Tech Lead
- [ ] Security Team  
- [ ] DevOps/Infra
- [ ] Frontend Team (cambios de API)

**Documentación Completa:** `ANALISIS_BACKEND_SEGURIDAD.md`

---

**Generado:** 5 de mayo de 2026  
**Nivel de Urgencia:** 🔴 **CRÍTICO - BLOQUEA PRODUCCIÓN**
