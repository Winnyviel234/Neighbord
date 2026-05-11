# Plan de Acción - Remediación de Vulnerabilidades de Seguridad

**Fecha de Creación:** 5 de mayo de 2026  
**Status:** 🔴 CRÍTICO - IMPLEMENTACIÓN INMEDIATA REQUERIDA  
**Timeline Estimado:** 3-4 semanas para remediación completa

---

## FASE 1: EMERGENCIA (Día 1 - 3 horas)

### Objetivo
Proteger los endpoints críticos públicos y websockets sin autenticación.

### Tareas

#### Task 1.1: Proteger GET /voting
**Archivo:** `backend/app/modules/voting/routes.py`  
**Línea:** 15  
**Cambio:**
```python
# ANTES
@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None)
):
    """Get all votings"""

# DESPUÉS
@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)  # ← AGREGAR
):
    """Get all votings"""
```
**Tiempo:** 5 minutos  
**Testing:**
```bash
# Antes: curl http://localhost:8000/api/v2/voting/ → 200 (vulnerable)
# Después: curl http://localhost:8000/api/v2/voting/ → 401 (protegido)
```

---

#### Task 1.2: Proteger GET /meetings
**Archivo:** `backend/app/modules/meetings/routes.py`  
**Líneas:** 11, 53  
**Cambio:**
```python
# GET /
# ANTES
@router.get("")
async def get_meetings(
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None)
):

# DESPUÉS
@router.get("")
async def get_meetings(
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)  # ← AGREGAR
):

# GET /{id}/attendances
# ANTES
@router.get("/{meeting_id}/attendances")
async def get_attendances(meeting_id: UUID):

# DESPUÉS
@router.get("/{meeting_id}/attendances")
async def get_attendances(
    meeting_id: UUID,
    user: dict = Depends(get_current_user)  # ← AGREGAR
):
```
**Tiempo:** 5 minutos

---

#### Task 1.3: Proteger GET /sectors
**Archivo:** `backend/app/modules/sectors/routes.py`  
**Líneas:** 9, 14  
**Cambio:**
```python
# GET /
# ANTES
@router.get("", response_model=List[SectorResponse])
async def get_sectors():
    """Get all sectors"""

# DESPUÉS
@router.get("", response_model=List[SectorResponse])
async def get_sectors(user: dict = Depends(get_current_user)):
    """Get all sectors"""

# GET /{id}
# ANTES
@router.get("/{sector_id}", response_model=SectorResponse)
async def get_sector(sector_id: UUID):
    """Get specific sector"""

# DESPUÉS
@router.get("/{sector_id}", response_model=SectorResponse)
async def get_sector(
    sector_id: UUID,
    user: dict = Depends(get_current_user)  # ← AGREGAR
):
    """Get specific sector"""
```
**Tiempo:** 5 minutos

---

#### Task 1.4: Proteger GET /fees
**Archivo:** `backend/app/modules/payments/routes.py`  
**Línea:** 44  
**Cambio:**
```python
# ANTES
@router.get("/fees")
async def get_fees():
    """Get active fees"""

# DESPUÉS
@router.get("/fees")
async def get_fees(user: dict = Depends(get_current_user)):
    """Get active fees"""
```
**Tiempo:** 5 minutos

---

#### Task 1.5: Deshabilitar o Proteger WebSocket /live
**Archivo:** `backend/app/main.py`  
**Opción A (Inmediato - Deshabilitar):**
```python
# Comentar la línea:
# app.include_router(live.router, prefix="/api")
```

**Opción B (Mejor - Proteger):**
**Archivo:** `backend/app/api/endpoints/live.py`  
```python
from fastapi import WebSocketException
from app.core.security import get_current_user_ws

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = Query(...)):
    """WebSocket endpoint con autenticación"""
    try:
        # Validar token
        user = verify_websocket_token(token)
        await websocket.accept()
        # ... resto del código
    except Exception as e:
        await websocket.close(code=1008, reason="Unauthorized")
```

**Tiempo:** 15 minutos (Opción B)

---

#### Task 1.6: Proteger Chat WebSocket
**Archivo:** `backend/app/modules/chat/routes.py`  
**Línea:** ~65  
**Similar a Task 1.5**  
**Tiempo:** 15 minutos

---

#### Task 1.7: Cambiar JWT Secret
**Archivo:** `backend/app/core/config.py`  
**Línea:** 15  
**Cambio:**
```python
# ANTES
jwt_secret_key: str = "cambia-esta-clave"

# DESPUÉS
jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "cambiar-en-produccion-" + secrets.token_urlsafe(32))
```

**Crear .env:**
```env
JWT_SECRET_KEY=tu-secret-aleatorio-muy-largo-y-complejo-de-64-caracteres-minimo
```

**Generar secret seguro:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Tiempo:** 10 minutos

---

#### Task 1.8: Deshabilitar WebSocket /live (Fallback)
Si no se implementa protección en 1.5, comentar en `main.py`:
```python
# Comentar:
# app.include_router(live.router, prefix="/api")
```
**Tiempo:** 2 minutos

---

### SUBTOTAL FASE 1
**Tiempo Total:** ~60-90 minutos  
**Risk Reduction:** 🔴 → 🟡

---

## FASE 2: SEGURIDAD PRIORITARIA (Semana 1 - 1-2 días)

### Objetivo
Implementar validaciones y seguridad básica.

#### Task 2.1: Agregar Validadores de Password
**Archivo:** `backend/app/modules/auth/model.py`  
**Cambio:**
```python
from pydantic import field_validator
import re

class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    documento: Optional[str] = None
    sector_id: Optional[str] = None
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe contener una letra mayúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password debe contener un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password debe contener un carácter especial')
        return v
    
    @field_validator('nombre')
    def validate_nombre(cls, v):
        if len(v) < 2:
            raise ValueError('Nombre debe tener al menos 2 caracteres')
        if len(v) > 100:
            raise ValueError('Nombre no puede exceder 100 caracteres')
        return v
```

**Tiempo:** 15 minutos

---

#### Task 2.2: Agregar Validadores de Payment
**Archivo:** `backend/app/modules/payments/model.py`  
**Cambio:**
```python
from pydantic import field_validator

class PaymentCreate(BaseModel):
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str = "efectivo"
    referencia: Optional[str] = None
    
    @field_validator('monto')
    def validate_monto(cls, v):
        if v <= 0:
            raise ValueError('Monto debe ser mayor a 0')
        if v > 1000000:
            raise ValueError('Monto no puede exceder 1,000,000')
        return round(v, 2)
    
    @field_validator('concepto')
    def validate_concepto(cls, v):
        if len(v) < 3:
            raise ValueError('Concepto debe tener al menos 3 caracteres')
        if len(v) > 200:
            raise ValueError('Concepto no puede exceder 200 caracteres')
        return v
    
    @field_validator('fecha_pago')
    def validate_fecha(cls, v):
        from datetime import date
        if v > date.today():
            raise ValueError('Fecha de pago no puede ser en el futuro')
        return v
```

**Tiempo:** 15 minutos

---

#### Task 2.3: Fix SQL Injection en votaciones.py
**Archivo:** `backend/app/api/endpoints/votaciones.py`  
**Línea:** 8-14  
**Cambio:**
```python
# ANTES
def _parse_election_option(option: str) -> dict[str, str]:
    parts = option.split("|")
    if not parts or parts[0] != "election":
        return {}
    values = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")
        values[key] = value
    return values

# DESPUÉS
def _parse_election_option(option: str) -> dict[str, str]:
    ALLOWED_FIELDS = {"user", "role"}
    ALLOWED_ROLES = {"directiva", "tesorero", "admin", "vecino"}
    
    parts = option.split("|")
    if not parts or parts[0] != "election":
        return {}
    
    values = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")
        
        # Validar campo permitido
        if key not in ALLOWED_FIELDS:
            continue  # Ignorar campos no permitidos
        
        # Validar valor según tipo de campo
        if key == "role" and value not in ALLOWED_ROLES:
            raise ValueError(f"Rol no permitido: {value}")
        
        # Validar UUID si es user
        if key == "user":
            try:
                UUID(value)  # Validar formato UUID
            except ValueError:
                raise ValueError(f"User ID debe ser UUID válido: {value}")
        
        values[key] = value
    
    return values
```

**Tiempo:** 20 minutos

---

#### Task 2.4: Agregar Rate Limiting Middleware
**Archivo:** `backend/app/main.py`  
**Cambio:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Después de imports
limiter = Limiter(key_func=get_remote_address)

# Agregar error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
    )

# Aplicar límites por endpoint
@app.get("/api/v2/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, payload: LoginRequest):
    ...

@app.post("/api/v2/auth/register")
@limiter.limit("3/minute")
async def register(request: Request, payload: RegisterRequest):
    ...

# Límite global más permisivo
@app.get("/api/health")
@limiter.limit("100/minute")
async def health(request: Request):
    ...
```

**Tiempo:** 20 minutos

---

#### Task 2.5: Agregar Security Headers
**Archivo:** `backend/app/main.py`  
**Cambio:**
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https:"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

**Tiempo:** 10 minutos

---

#### Task 2.6: Mejorar CORS
**Archivo:** `backend/app/main.py`  
**Línea:** 25-31  
**Cambio:**
```python
# ANTES
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DESPUÉS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$" if settings.environment == "development" else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # ← Específico
    allow_headers=["Content-Type", "Authorization", "Accept"],  # ← Específico
    expose_headers=["Content-Length", "Content-Range"],
    max_age=3600,
)
```

**Tiempo:** 10 minutos

---

#### Task 2.7: Sanitizar Chat Messages
**Archivo:** `backend/app/modules/chat/service.py`  
**Cambio:**
```bash
# Instalar bleach
pip install bleach
```

```python
import bleach

# En send_message()
def send_message(self, room_id: UUID, payload: MessageCreate, user: dict):
    # Sanitizar contenido
    clean_content = bleach.clean(payload.content, strip=True, tags=[], strip_comments=True)
    
    # Limitar a 500 caracteres
    if len(clean_content) > 500:
        clean_content = clean_content[:500]
    
    # Crear mensaje con contenido limpio
    return db.insert({
        ...
        "content": clean_content,
        ...
    })
```

**Tiempo:** 10 minutos

---

### SUBTOTAL FASE 2
**Tiempo Total:** ~120 minutos (2 horas)  
**Risk Reduction:** 🟡 → 🟠

---

## FASE 3: CONSOLIDACIÓN (Semana 2)

### Objetivo
Eliminar duplicación y mejorar consistencia.

#### Task 3.1: Crear Migration Plan para Legacy Endpoints
- [ ] Documentar todos los clientes de endpoints legacy
- [ ] Crear plan de migración por cliente
- [ ] Implementar deprecation headers
- [ ] Establecer fecha de obsolescencia

**Tiempo:** 1-2 días

---

#### Task 3.2: Consolidar Modelos Duplicados
- [ ] Revisar `PaymentCreate` (duplicado en payments/model.py)
- [ ] Revisar otros modelos duplicados
- [ ] Crear helpers comunes

**Tiempo:** 4 horas

---

#### Task 3.3: Implementar Tests de Seguridad
```bash
# Instalar pytest y fixtures
pip install pytest pytest-asyncio httpx

# Tests básicos
pytest backend/tests/security/ -v
```

**Tiempo:** 2-3 días

---

#### Task 3.4: Implementar Logging de Seguridad
- [ ] Log de intentos de acceso no autorizados
- [ ] Log de cambios sensibles
- [ ] Log de errores de autenticación
- [ ] Integración con SIEM (opcional)

**Tiempo:** 1-2 días

---

### SUBTOTAL FASE 3
**Tiempo Total:** 4-6 días  
**Risk Reduction:** 🟠 → 🟢

---

## FASE 4: TESTING Y VALIDACIÓN (Semana 3)

### Objective
Validar todas las correcciones y realizar penetration testing.

#### Task 4.1: Security Audit Checklist
```bash
# OWASP Top 10 2021
[ ] A01:2021 - Broken Access Control
[ ] A02:2021 - Cryptographic Failures
[ ] A03:2021 - Injection
[ ] A04:2021 - Insecure Design
[ ] A05:2021 - Security Misconfiguration
[ ] A06:2021 - Vulnerable and Outdated Components
[ ] A07:2021 - Identification and Authentication Failures
[ ] A08:2021 - Software and Data Integrity Failures
[ ] A09:2021 - Logging and Monitoring Failures
[ ] A10:2021 - Server-Side Request Forgery (SSRF)
```

**Tiempo:** 1 día

---

#### Task 4.2: Penetration Testing
- [ ] OWASP ZAP Scan
- [ ] Burp Suite Community (si disponible)
- [ ] Manual testing de endpoints críticos
- [ ] Fuzzing de inputs

**Tiempo:** 2-3 días

---

#### Task 4.3: Code Review de Seguridad
- [ ] Review completo de /app/modules
- [ ] Review completo de /app/api/endpoints
- [ ] Review de configuración
- [ ] Review de servicios

**Tiempo:** 2-3 días

---

### SUBTOTAL FASE 4
**Tiempo Total:** 5-7 días  
**Risk Reduction:** 🟢 ✅

---

## TIMELINE GENERAL

```
Día 1 (Hoy):           FASE 1 - Emergency (3 horas) → 🟡
Semana 1:              FASE 2 - Priority (2 días)   → 🟠
Semana 2:              FASE 3 - Consolidation       → 🟢
Semana 3-4:            FASE 4 - Validation          → ✅

Total: 3-4 semanas para remediación completa
```

---

## RECURSOS REQUERIDOS

- [ ] 1 Senior Backend Developer (4 semanas, 50%)
- [ ] 1 Security Engineer (2 semanas, 25%)
- [ ] 1 QA/Tester (2 semanas, 50%)
- [ ] Access a OWASP ZAP o Burp Suite
- [ ] Staging environment para testing

---

## MÉTRICAS DE ÉXITO

✅ Todas las vulnerabilidades críticas (12) mitigadas  
✅ Rate limiting implementado globalmente  
✅ Security headers agregados  
✅ Tests de seguridad pasados  
✅ Zero high-severity findings en audit  
✅ OWASP Top 10 compliance validado  

---

## SIGN-OFF

**Aprobado por:** [Pendiente]  
**Fecha de Inicio:** [Pendiente]  
**Fecha de Término Esperada:** [Pendiente]  
**Status:** 🟡 EN ESPERA DE APROBACIÓN

---

**Documento Preparado:** 5 de mayo de 2026  
**Versión:** 1.0  
**Urgencia:** 🔴 CRÍTICA
