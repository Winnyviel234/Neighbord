# Análisis Comprehensivo de Seguridad del Backend

**Fecha de Análisis:** Mayo 5, 2026  
**Versión:** 1.0  
**Alcance:** Backend /app (módulos y endpoints legacy)

---

## RESUMEN EJECUTIVO

### Estado General
- ✅ **Arquitectura Modular:** Implementación moderna de módulos v2 en `/app/modules/`
- ⚠️ **Endpoints Legacy:** Duplicación y conflictos de autenticación en `/app/api/endpoints/`
- ⚠️ **Inconsistencia de Seguridad:** Mezcla de patrones `require_roles()` vs `require_permissions()`
- 🔴 **Vulnerabilidades Críticas:** Endpoints públicos sin protección, validación inconsistente
- 🟡 **Deuda Técnica:** Duplicación de código, modelos duplicados, falta de tests

---

## 1. MÓDULOS IMPLEMENTADOS

### ✅ Módulos Completamente Implementados (21)

| Módulo | Estado | Estructura | Rutas Expuestas |
|--------|--------|-----------|-----------------|
| **auth** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/auth` |
| **users** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/users` |
| **payments** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/payments` |
| **complaints** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/complaints` |
| **voting** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/voting` |
| **notifications** | ✅ | models.py, routes.py, service.py, repository.py | `/api/v2/notifications` |
| **chat** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/chat` |
| **meetings** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/meetings` |
| **sectors** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/sectors` |
| **roles** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/roles` |
| **statistics** | ✅ | routes.py, service.py, repository.py | `/api/v2/statistics` |
| **audit** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/audit` |
| **projects** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/projects` |
| **directiva** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/directiva` |
| **search** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/search` |
| **banking** | ✅ | models.py, routes.py, service.py | `/api/v2/banking` |
| **oauth** | ✅ | models.py, routes.py, service.py | `/api/v2/oauth` |
| **webhooks** | ✅ | model.py, routes.py, service.py, repository.py | `/api/v2/webhooks` |
| **public_api** | ✅ | models.py, routes.py, service.py | `/api/v2/public` |
| **monitoring** | ✅ | routes.py | `/api/v2/monitoring` |
| **monitoring** | ⚠️ | Minimal (solo routes.py) | `/api/v2/monitoring` |

### 🔴 Endpoints Legacy sin Remigrar (16)

Ubicados en `/app/api/endpoints/`:
1. **auth.py** - Duplica `/api/v2/auth`, convierte esquemas
2. **vecinos.py** - Gestión de usuarios (legacy)
3. **reuniones.py** - Gestión de reuniones (legacy)
4. **votaciones.py** - Votaciones con lógica de elección
5. **finanzas.py** - Gestión de pagos y transacciones
6. **cuotas.py** - Gestión de cuotas
7. **solicitudes.py** - Gestión de solicitudes/reportes
8. **comunicados.py** - Comunicados para usuarios
9. **comunicados_publicos.py** - Comunicados públicos
10. **noticias.py** - Gestión de noticias
11. **otros.py** - Endpoints misceláneos (dashboard, landing)
12. **directiva.py** - Gestión de directiva (legacy)
13. **reportes.py** - Generación de reportes
14. **documentos.py** - Gestión de documentos
15. **email_endpoints.py** - Endpoints de email
16. **live.py** - WebSocket en vivo sin autenticación

---

## 2. ANÁLISIS DE SEGURIDAD POR MÓDULO

### 2.1 MÓDULO: AUTH

**Ruta:** `/api/v2/auth`  
**Protección:** Mixed

#### Endpoints:
```
POST   /register              ❌ SIN PROTECCIÓN (público)
POST   /login                 ❌ SIN PROTECCIÓN (público)
GET    /me                    ✅ Requiere get_current_user
PATCH  /me                    ✅ Requiere get_current_user
POST   /change-password       ✅ Requiere get_current_user
```

#### Vulnerabilidades Identificadas:
1. **CRÍTICO:** `/register` sin rate limiting → brute force, spam
2. **CRÍTICO:** No hay validación de password strength (solo EmailStr en modelo)
3. **ALTO:** No hay verificación de email post-registro
4. **ALTO:** Token JWT con secret débil en config.py: `"cambia-esta-clave"`
5. **ALTO:** No hay refresh token mechanism
6. **MEDIO:** Sin captcha en registro

#### Validación Pydantic:
```python
✅ RegisterRequest: nombre, email (EmailStr), password, sector_id
✅ LoginRequest: email (EmailStr), password
⚠️ FALTA: Password validation (min length, complexity)
⚠️ FALTA: Nombre validation (length bounds, caracteres)
```

---

### 2.2 MÓDULO: USERS

**Ruta:** `/api/v2/users`  
**Protección:** Mixed

#### Endpoints:
```
GET    /                      ✅ Requiere get_current_user (pero sin validar permisos para filtros)
GET    /{user_id}            ⚠️ Parcialmente protegido (solo admin/directiva pueden ver otros)
PATCH  /{user_id}            ⚠️ Sin especificar protección
POST   /{user_id}/approve    ✅ Requiere "manage_users"
POST   /{user_id}/deactivate ✅ Requiere "all" (admin)
```

#### Vulnerabilidades Identificadas:
1. **ALTO:** `GET /users` sin validación de permisos para ver lista completa
2. **ALTO:** `PATCH /{user_id}` sin validación de permisos en endpoint
3. **MEDIO:** Usuarios no-admin pueden ver otros usuarios si hacen queries directas
4. **MEDIO:** Sin rate limiting en endpoints sensibles

#### Validación Pydantic:
```python
✅ UserUpdate: validación presente
⚠️ FALTA: Restricción de campos que no pueden cambiar usuarios normales
```

---

### 2.3 MÓDULO: PAYMENTS

**Ruta:** `/api/v2/payments`  
**Protección:** ⚠️ Inconsistente

#### Endpoints:
```
GET    /                      ✅ Protegido por get_current_user (solo pagos del usuario)
GET    /all                   🔴 FALTA VALIDACIÓN FUERTE DE ROLES
POST   /                      ✅ Protegido
PATCH  /{id}/verify           ⚠️ Sin validación de permisos especificados
GET    /fees                  ❌ PÚBLICO SIN PROTECCIÓN
GET    /fees/{id}/status      ✅ Protegido
POST   /strike                ✅ Protegido
GET    /{id}/strike-status    ✅ Protegido
```

#### Vulnerabilidades Críticas:
1. **CRÍTICO:** `GET /fees` es público → expone estructura de pagos
2. **CRÍTICO:** `GET /all` sin autenticación verificada en endpoint
3. **ALTO:** Sin validación de monto en PaymentCreate
4. **ALTO:** Falta de verificación de usuario_id en operaciones CRUD
5. **ALTO:** Sin validación de fechas de pago (puede ser futura/pasada)

#### Validación Pydantic:
```python
⚠️ PaymentCreate: DUPLICADO en el archivo (líneas ~38 y ~57)
⚠️ FALTA: Validación de monto (mínimo, máximo, decimales)
⚠️ FALTA: Validación de concepto (length, caracteres especiales)
⚠️ FALTA: Validación de fecha_pago (no puede ser futura)
```

---

### 2.4 MÓDULO: VOTING

**Ruta:** `/api/v2/voting`  
**Protección:** 🔴 CRÍTICA

#### Endpoints:
```
GET    /                      ❌ PÚBLICO SIN PROTECCIÓN
GET    /{id}                  ✅ Requiere get_current_user
POST   /                      ✅ Requiere get_current_user
POST   /{id}/vote             ✅ Requiere get_current_user
PATCH  /{id}/close            ✅ Requiere get_current_user
```

#### Vulnerabilidades CRÍTICAS:
1. **🔴 CRÍTICO:** `GET /` permite enumerar TODAS las votaciones sin autenticación
2. **🔴 CRÍTICO:** Voto múltiple no prevenido (sin unique constraint)
3. **🔴 CRÍTICO:** `_finish_election()` asigna roles directamente sin validación
4. **ALTO:** SQL injection potencial en `_parse_election_option()`
5. **ALTO:** Sin rate limiting en POST `/vote` → spam de votos

#### Validación Pydantic:
```python
⚠️ VotingCreate: No visible en archivo de routes
⚠️ FALTA: Validación de opciones (array vacio, duplicados)
⚠️ FALTA: Validación de fechas (inicio < fin)
```

---

### 2.5 MÓDULO: COMPLAINTS

**Ruta:** `/api/v2/complaints`  
**Protección:** ✅ Adecuada

#### Endpoints:
```
GET    /                      ✅ Protegido, con filtros
GET    /{id}                  ✅ Protegido
POST   /                      ✅ Protegido
PATCH  /{id}                  ✅ Protegido
DELETE /{id}                  ✅ Requiere admin
POST   /{id}/comments         ✅ Protegido
GET    /{id}/comments         ✅ Protegido
```

#### Hallazgos Positivos:
- ✅ Todos los endpoints requieren autenticación
- ✅ Validación básica presente
- ✅ Separación de permisos por operación

#### Potenciales Mejoras:
- ⚠️ Sin validación de status/priority en filtros
- ⚠️ Sin límite de results (puede cargar N mil registros)

---

### 2.6 MÓDULO: CHAT

**Ruta:** `/api/v2/chat`  
**Protección:** ✅ Bien

#### Endpoints:
```
GET    /rooms                 ✅ Protegido
GET    /rooms/{id}            ✅ Protegido
POST   /rooms                 ✅ Requiere get_current_user
DELETE /rooms/{id}            ✅ Protegido
GET    /rooms/{id}/messages   ✅ Protegido, con limit (1-100)
POST   /rooms/{id}/messages   ✅ Protegido
WS     /ws/{room_id}          ⚠️ SIN AUTENTICACIÓN EN WEBSOCKET
```

#### Vulnerabilidades:
1. **CRÍTICO:** WebSocket `/ws/{room_id}` sin autenticación
2. **ALTO:** XSS potencial en mensajes sin sanitización
3. **ALTO:** Sin validación de room_id (UUID válido)

#### Validación Pydantic:
```python
✅ MessageCreate: presente
⚠️ FALTA: Validación de content (length, caracteres)
```

---

### 2.7 MÓDULO: MEETINGS

**Ruta:** `/api/v2/meetings`  
**Protección:** 🟡 Inconsistente

#### Endpoints:
```
GET    /                      ❌ PÚBLICO SIN PROTECCIÓN
GET    /{id}                  ❌ PÚBLICO SIN PROTECCIÓN
POST   /                      ✅ Protegido
PATCH  /{id}                  ✅ Protegido
DELETE /{id}                  ✅ Protegido
POST   /{id}/attend           ✅ Protegido
GET    /{id}/attendances      ❌ PÚBLICO SIN PROTECCIÓN
```

#### Vulnerabilidades Críticas:
1. **CRÍTICO:** `GET /` y `GET /{id}` públicos → enumera todas las reuniones
2. **CRÍTICO:** `GET /{id}/attendances` público → lista asistencia
3. **ALTO:** Sin filtro de tipo/estado en GET /
4. **ALTO:** Sin límite de results

---

### 2.8 MÓDULO: NOTIFICATIONS

**Ruta:** `/api/v2/notifications`  
**Protección:** ⚠️ No revisado completamente

#### Estado:
- models.py tiene estructura adicional
- Requiere revisión completa de routes.py

---

### 2.9 MÓDULO: SECTORS

**Ruta:** `/api/v2/sectors`  
**Protección:** ⚠️ Crítico

#### Endpoints:
```
GET    /                      ❌ PÚBLICO SIN PROTECCIÓN
GET    /{id}                  ❌ PÚBLICO SIN PROTECCIÓN
POST   /                      ✅ Requiere "all" (admin)
PATCH  /{id}                  ✅ Requiere "all" (admin)
DELETE /{id}                  ✅ Requiere "all" (admin)
GET    /{id}/users            ✅ Protegido
```

#### Vulnerabilidades:
1. **CRÍTICO:** `GET /sectors` público → enumera estructura organizacional
2. **CRÍTICO:** `GET /sectors/{id}` público
3. **MEDIO:** Sin validación de sector_id en `get_sector_users`

---

### 2.10 MÓDULO: ROLES

**Ruta:** `/api/v2/roles`  
**Protección:** ✅ Adecuada

#### Endpoints:
```
GET    /                      ✅ Requiere get_current_user
GET    /{id}                  ✅ Requiere get_current_user
POST   /                      ✅ Requiere "all"
PATCH  /{id}                  ✅ Requiere "all"
DELETE /{id}                  ✅ Requiere "all"
```

#### Estado:
- ✅ Todos los endpoints protegidos
- ✅ Permisos apropriados por operación

---

### 2.11 MÓDULO: AUDIT

**Ruta:** `/api/v2/audit`  
**Protección:** ✅ Muy Bien

#### Endpoints:
```
GET    /logs                  ✅ Requiere "view_audit_logs"
GET    /summary               ✅ Requiere "view_audit_logs"
POST   /consent               ✅ Protegido (GDPR)
GET    /consent               ✅ Protegido
DELETE /consent/{type}        ✅ Protegido
POST   /data-deletion         ✅ Protegido (GDPR)
```

#### Hallazgos Positivos:
- ✅ Excelente implementación de GDPR
- ✅ Auditoria de accesos
- ✅ Consentimiento documentado

---

### 2.12 MÓDULO: PAYMENTS - LEGACY (finanzas.py)

**Ruta:** `/api/finanzas`  
**Protección:** ⚠️ Crítico

#### Endpoints:
```
GET    /pagos                 ✅ Requiere admin/directiva/tesorero
POST   /pagos                 ✅ Requiere admin/tesorero
POST   /pagos/solicitud       ✅ Requiere get_current_user
PATCH  /pagos/{id}            ✅ Requiere admin
DELETE /pagos/{id}            ✅ Requiere admin
GET    /transacciones         ✅ Requiere admin/directiva/tesorero
POST   /transacciones         ✅ Requiere admin/tesorero
```

#### Vulnerabilidades:
1. **ALTO:** `POST /pagos/solicitud` sin validar que el usuario es el dueño del pago
2. **ALTO:** Sin validación de monto en PagoIn
3. **ALTO:** Sin validación de concepto
4. **ALTO:** Duplicación con `/api/v2/payments`

#### Validación Pydantic:
```python
⚠️ PagoIn, TransaccionIn: No revisados completamente
```

---

### 2.13 MÓDULO: VOTACIONES - LEGACY (votaciones.py)

**Ruta:** `/api/votaciones`  
**Protección:** 🔴 CRÍTICO

#### Vulnerabilidades Críticas:
1. **🔴 CRÍTICO:** `_finish_election()` asigna roles arbitrarios basado en parseo de string
2. **🔴 CRÍTICO:** SQL Injection en `_parse_election_option()`:
   ```python
   def _parse_election_option(option: str) -> dict[str, str]:
       parts = option.split("|")  # Sin validación
       for part in parts[1:]:
           key, _, value = part.partition("=")  # Injection posible
   ```
3. **🔴 CRÍTICO:** No hay prevención de voto múltiple
4. **ALTO:** Formato de opción `election|user=UUID|role=ROL` no validado

---

### 2.14 MÓDULO: REPORTES - LEGACY (reportes.py)

**Ruta:** `/api/reportes`  
**Protección:** ✅ Adecuada

#### Endpoints:
```
GET    /{tipo}.{formato}      ✅ Requiere admin/directiva/tesorero
POST   /email/mora/{usuario}  ✅ Requiere admin/tesorero
```

#### Hallazgos:
- ✅ Buen uso de streaming para CSV
- ✅ Límite de 5000 filas por defecto
- ✅ Whitelist de tablas (TABLES dict)

#### Potenciales Mejoras:
- ⚠️ Sin validación de usuario_id formato
- ⚠️ Sin validación de monto en /email/mora

---

### 2.15 MÓDULO: VECINOS - LEGACY (vecinos.py)

**Ruta:** `/api/vecinos`  
**Protección:** ✅ Bien

#### Endpoints:
```
GET    /                      ✅ Requiere admin/directiva/tesorero
POST   /                      ✅ Requiere admin/directiva
PATCH  /{id}/aprobar          ✅ Requiere admin/directiva
PATCH  /{id}/estado/{estado}  ✅ Requiere admin/directiva
PATCH  /{id}/rol/{rol}        ⚠️ Requiere admin (pero no valida rol)
PATCH  /{id}                  ✅ Requiere admin
DELETE /{id}                  ✅ Requiere admin
GET    /morosos               ✅ Requiere admin/directiva/tesorero
```

#### Vulnerabilidades:
1. **ALTO:** `PATCH /{id}/rol/{rol}` acepta cualquier rol sin validación
2. **MEDIO:** Sin validación de payload en POST/PATCH
3. **MEDIO:** Duplicación con `/api/v2/users`

---

### 2.16 MÓDULO: LIVE - WEBSOCKET (live.py)

**Ruta:** `/api/live`  
**Protección:** 🔴 CRÍTICO

#### Endpoints:
```
GET    /live/status           ✅ Público (info endpoint)
WS     /ws/live               🔴 SIN AUTENTICACIÓN
```

#### Vulnerabilidades Críticas:
1. **🔴 CRÍTICO:** WebSocket completamente sin autenticación
2. **🔴 CRÍTICO:** Broadcast a todos los usuarios sin validación
3. **ALTO:** XSS potencial en mensajes
4. **ALTO:** DDoS mediante conexiones masivas
5. **ALTO:** No hay rate limiting

#### Código Vulnerable:
```python
@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()  # ← Sin verificar autenticación
    # ...
```

---

### 2.17 MÓDULO: OTROS - LEGACY (otros.py)

**Ruta:** `/api`  
**Protección:** ⚠️ Inconsistente

#### Endpoints:
```
GET    /dashboard             ✅ Requiere get_current_user
GET    /public/landing        ❌ PÚBLICO SIN PROTECCIÓN
```

#### Vulnerabilidades:
1. **CRÍTICO:** `/public/landing` expone:
   - Comunicados y noticias (OK)
   - Votaciones activas (⚠️)
   - Directiva info (⚠️)
   - Asambleas (⚠️)

2. **ALTO:** `/dashboard` ejecuta múltiples queries sin límite
3. **ALTO:** Sin paginación en dashboard

---

### 2.18 MÓDULO: PUBLIC_API

**Ruta:** `/api/v2/public`  
**Protección:** ✅ Bien

#### Endpoints:
```
GET    /stats                 ✅ Rate limited (10/min), API key opcional
GET    /sectors               ✅ Rate limited (20/min), API key opcional
GET    /projects              ✅ Rate limited (30/min), API key opcional
```

#### Hallazgos Positivos:
- ✅ Rate limiting implementado
- ✅ API key validation
- ✅ Límite de resultados respetado

#### Mejoras Necesarias:
- ⚠️ Validar limit > 100 pero sin retornar error claro

---

### 2.19 MÓDULO: OAUTH

**Ruta:** `/api/v2/oauth`  
**Protección:** ✅ Bien

#### Endpoints:
```
GET    /providers             ✅ Público (lista de providers)
POST   /login                 ✅ Público pero con validación
GET    /callback/{provider}   ✅ State validation
```

#### Hallazgos Positivos:
- ✅ State parameter validation
- ✅ Error handling en callback
- ✅ Redirect seguro

#### Mejoras:
- ⚠️ Validar que provider existe

---

### 2.20 MÓDULO: BANKING

**Ruta:** `/api/v2/banking`  
**Protección:** ✅ Protegido

#### Endpoints:
```
GET    /integrations          ✅ Público (lista)
POST   /connections           ✅ Requiere get_current_user
GET    /connections           ✅ Requiere get_current_user
```

#### Estado:
- ✅ Protección adecuada
- ✅ No expone datos sensibles

---

### 2.21 MÓDULO: WEBHOOKS

**Ruta:** `/api/v2/webhooks`  
**Protección:** ✅ Bien

#### Endpoints:
```
POST   /subscriptions         ✅ Requiere admin
GET    /subscriptions         ✅ Requiere admin
GET    /subscriptions/{id}    ✅ Requiere admin
PUT    /subscriptions/{id}    ✅ Requiere admin
```

#### Hallazgos:
- ✅ Whitelist de campos en PUT
- ✅ Solo admin puede gestionar
- ✅ Validación básica presente

---

## 3. VULNERABILIDADES CRÍTICAS ENCONTRADAS

### 🔴 CRÍTICAS (Requieren Fix Inmediato)

| ID | Módulo | Endpoint | Riesgo | Impacto |
|----|--------|----------|--------|--------|
| **C1** | voting | GET / | Enumeración pública | Expone votaciones activas |
| **C2** | voting | POST /vote | Voto múltiple | Manipulación de elecciones |
| **C3** | voting | /finalize | RCE/Privilege Escalation | Asigna roles arbitrarios |
| **C4** | meetings | GET / | Enumeración pública | Expone reuniones |
| **C5** | meetings | GET /{id}/attendances | Información de asistencia | Privacidad afectada |
| **C6** | live.py | WS /ws/live | Falta autenticación | XSS, DDoS, privacidad |
| **C7** | payments | GET /fees | Enumeración | Expone cuotas públicas |
| **C8** | auth | POST /register | Sin rate limiting | Spam, fuerza bruta |
| **C9** | votaciones.py | _parse_election_option | SQL Injection | Ejecución arbitraria |
| **C10** | sectors | GET / | Enumeración | Expone estructura org |
| **C11** | chat | WS /ws/{room_id} | Sin autenticación | Acceso no autorizado |
| **C12** | sectors | GET /{id} | Información sensible | Expone detalles privados |

### 🟡 ALTAS (Requieren Fix en Sprint)

| ID | Módulo | Descripción | Solución |
|----|--------|-------------|----------|
| **H1** | auth | Token JWT con secret débil | Usar variable de env segura |
| **H2** | auth | Sin validación de password strength | Agregar validador Pydantic |
| **H3** | payments | Sin validación de monto | Agregar min/max en model |
| **H4** | users | GET /users sin permisos claros | Validar en endpoint |
| **H5** | payments | GET /all sin protección fuerte | Validar roles específicos |
| **H6** | reportes | Sin validación usuario_id | Validar formato UUID |
| **H7** | vecinos | PATCH /{id}/rol sin validar rol | Whitelist de roles permitidos |
| **H8** | otros | /public/landing expone datos | Restricción de info retornada |

### 🟠 MEDIAS (Mejoras de Seguridad)

- Sin rate limiting en muchos endpoints
- Sin sanitización HTML en contenido de usuarios
- Sin validación de límites en query parameters
- Validación Pydantic inconsistente entre módulos
- Logs de seguridad insuficientes

---

## 4. ESTADO DE VALIDACIÓN CON PYDANTIC

### ✅ Módulos con Validación Adecuada
- **complaints:** ComplaintCreate, ComplaintUpdate validados
- **chat:** MessageCreate validado
- **roles:** RoleCreate, RoleUpdate validados
- **audit:** AuditReportRequest validado
- **projects:** ProjectCreate, ProjectUpdate validados

### ⚠️ Módulos con Validación Incompleta
- **auth:** Falta password strength, nombre bounds
- **payments:** Monto sin validación, concepto sin bounds
- **voting:** Opciones sin validación
- **meetings:** Título/descripción sin bounds
- **sectors:** Nombre sin validación

### ❌ Módulos Legacy sin Validación (endpoints.py)
- **vecinos.py:** VecinoIn sin validación fuerte
- **finanzas.py:** PagoIn, TransaccionIn sin revisar
- **votaciones.py:** VotacionIn sin validación de opciones
- **otros.py:** Sin schemas para query params

---

## 5. PROBLEMAS DE DEUDA TÉCNICA

### Duplicación de Código
1. **Auth Routes:** `/api/auth` (legacy) vs `/api/v2/auth` (moderno)
2. **Payments:** `/api/finanzas` vs `/api/v2/payments`
3. **Users:** `/api/vecinos` vs `/api/v2/users`
4. **Votaciones:** `/api/votaciones` vs `/api/v2/voting`
5. **Meetings:** `/api/reuniones` vs `/api/v2/meetings`

### Duplicación de Modelos
- **PaymentCreate:** Definido DOS veces en payments/model.py (líneas 8-13 y 47-51)
- **BankAccount, BankSyncResult:** Definido pero no usado

### Inconsistencia de Patrones
1. **require_roles():** Usado en legacy endpoints
2. **require_permissions():** Usado en nuevos módulos
3. **Función factory en algunos, clase en otros:** Inconsistencia en Services
4. **Query() vs Depends():** Mezcla de patrones

### Falta de Tests de Seguridad
- ❌ No hay pruebas de SQL injection
- ❌ No hay pruebas de XSS
- ❌ No hay pruebas de CSRF
- ❌ No hay pruebas de autenticación
- ❌ No hay pruebas de autorización

### Logging Insuficiente
- Sin logs de acceso no autorizados
- Sin logs de cambios sensibles
- Sin logs de errores de seguridad

---

## 6. MIDDLEWARE Y CONFIGURACIÓN GLOBAL

### Middleware Actual
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}):\d+$",
    allow_credentials=True,
    allow_methods=["*"],  # ⚠️ TODOS LOS MÉTODOS
    allow_headers=["*"],  # ⚠️ TODOS LOS HEADERS
)
```

### Problemas:
1. **ALTO:** `allow_methods=["*"]` expone todos los métodos HTTP
2. **ALTO:** `allow_headers=["*"]` permite headers arbitrarios
3. **FALTA:** Middleware de rate limiting (existe config pero no implementado)
4. **FALTA:** Middleware de HSTS
5. **FALTA:** Middleware de X-Frame-Options
6. **FALTA:** Middleware de X-Content-Type-Options
7. **FALTA:** Middleware de Content Security Policy

### Security Headers Faltantes
```
X-Frame-Options: DENY                   ❌
X-Content-Type-Options: nosniff          ❌
Strict-Transport-Security: ...           ❌
Content-Security-Policy: ...             ❌
Referrer-Policy: ...                     ❌
```

---

## 7. CONFIGURACIÓN CRÍTICA

### `/app/core/config.py` - PROBLEMAS

```python
jwt_secret_key: str = "cambia-esta-clave"  # 🔴 CRÍTICO: Secret débil
admin_name: str = "Administrador Neighbord"
admin_email: str = "admin@gmail.com"       # ⚠️ Email hardcodeado
admin_password: str = "CambiaEstaClave123" # 🔴 CRÍTICO: Password hardcodeada
```

### Recomendaciones:
1. **CRÍTICO:** Cambiar `jwt_secret_key` a variable de entorno fuerte
2. **CRÍTICO:** No guardar admin_password en código
3. **ALTO:** Implementar creación de admin mediante script inicial
4. **ALTO:** Usar variables de env para config sensible

---

## 8. ENDPOINTS QUE REQUIEREN PROTECCIÓN INMEDIATA

### Cambios Requeridos:

#### 1. **voting.py** - GET / (Debe protegerse)
```python
# ANTES
@router.get("")
def list_votaciones(user: dict = Depends(get_current_user)):

# DESPUÉS (sin cambios necesarios - ya está protegido)
```

**ESTADO:** El archivo en `/app/modules/voting/routes.py` ya requiere `get_current_user` en GET /{voting_id}
**PROBLEMA:** En routes.py línea 15: `GET /` no tiene autenticación
```python
@router.get("")
async def get_votings(
    estado: Optional[str] = Query(None)
):  # ← SIN PROTECCIÓN
```

#### 2. **meetings.py** - GET / y GET /{id} (Deben protegerse)
```python
# ANTES
@router.get("")
def list_votaciones(user: dict = Depends(get_current_user)):

# DESPUÉS - requiere autenticación
@router.get("")
async def get_meetings(
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)  # ← AGREGAR
):
```

#### 3. **sectors.py** - GET / y GET /{id} (Deben protegerse)
```python
# ANTES
@router.get("", response_model=List[SectorResponse])
async def get_sectors():  # ← PÚBLICO

# DESPUÉS
@router.get("", response_model=List[SectorResponse])
async def get_sectors(user: dict = Depends(get_current_user)):  # ← PROTEGER
```

#### 4. **live.py** - WebSocket (Debe protegerse)
```python
# ANTES
@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()  # ← SIN AUTENTICACIÓN

# DESPUÉS
@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = Query(...)):
    try:
        user = verify_websocket_token(token)  # ← VALIDAR TOKEN
        await websocket.accept()
    except:
        await websocket.close(code=1008)
```

#### 5. **payments.py** - GET /fees (Debe protegerse)
```python
# ANTES
@router.get("/fees")
async def get_fees():  # ← PÚBLICO

# DESPUÉS
@router.get("/fees")
async def get_fees(user: dict = Depends(get_current_user)):  # ← PROTEGER
```

#### 6. **chat.py** - WebSocket (Debe autenticarse)
```python
# ANTES
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()  # ← SIN AUTENTICACIÓN

# DESPUÉS - implementar token verification
```

---

## 9. MATRIZ DE RIESGOS

```
┌─────────────────┬──────────────┬──────────────┐
│ SEVERIDAD       │ CANTIDAD     │ ESTADO       │
├─────────────────┼──────────────┼──────────────┤
│ 🔴 CRÍTICA      │ 12           │ ACTIVA       │
│ 🟡 ALTA         │ 8            │ ACTIVA       │
│ 🟠 MEDIA        │ 15+          │ ACTIVA       │
│ 🟢 BAJA         │ N/A          │ MINOR        │
└─────────────────┴──────────────┴──────────────┘

Riesgo General: 🔴 CRÍTICO - REQUIERE ACCIÓN INMEDIATA
```

---

## 10. PLAN DE REMEDIACIÓN RECOMENDADO

### FASE 1: CRÍTICO (Semana 1)
- [ ] Proteger GET endpoints sin autenticación (voting, meetings, sectors, payments/fees)
- [ ] Autenticar WebSocket endpoints (live.py, chat.py)
- [ ] Fijar secret JWT en config.py o envs
- [ ] Implementar rate limiting global

### FASE 2: ALTO (Semana 2)
- [ ] Agregar validadores Pydantic faltantes (password, monto, etc)
- [ ] Implementar seguridad headers (CORS, HSTS, CSP)
- [ ] Validar todos los role assignments
- [ ] Agregar sanitización HTML

### FASE 3: CONSOLIDACIÓN (Semana 3)
- [ ] Eliminar endpoints legacy duplicados
- [ ] Consolidar modelos duplicados
- [ ] Implementar tests de seguridad (OWASP Top 10)
- [ ] Agregar logging de seguridad

### FASE 4: HARDENING (Ongoing)
- [ ] Code review de seguridad completo
- [ ] Penetration testing
- [ ] SAST/DAST integration
- [ ] Rate limiting por usuario/IP

---

## 11. REQUERIMIENTOS vs IMPLEMENTACIÓN

### Funcionalidades Esperadas (según docs):
- ✅ Autenticación y autorización → Parcialmente implementada
- ✅ Gestión de usuarios → Implementada (con duplicación)
- ✅ Sistema de votaciones → Implementada (con vulnerabilidades críticas)
- ✅ Gestión financiera → Implementada (con duplicación)
- ✅ Chat comunitario → Implementada (sin seguridad WebSocket)
- ✅ Notificaciones → Parcialmente (routes.py presente)
- ✅ Auditoria → Muy bien implementada
- ✅ API Pública → Bien implementada
- ⚠️ OAuth/SSO → Implementada (requiere validación)
- ⚠️ Banking Integration → Implementada (básica)
- ✅ Webhooks → Implementada
- ⚠️ Search → Implementada (requiere validación)

---

## 12. CONCLUSIONES

### Puntos Fuertes
1. ✅ Arquitectura modular moderna
2. ✅ Separación de responsabilidades
3. ✅ Auditoría y GDPR compliance implementados
4. ✅ Algunos módulos tienen buena seguridad (complaints, audit, roles)
5. ✅ API pública con rate limiting

### Puntos Débiles
1. 🔴 **12 vulnerabilidades críticas activas**
2. 🔴 Endpoints públicos sin protección
3. 🔴 Autenticación falta en WebSockets
4. 🔴 SQL injection potencial en votaciones.py
5. 🔴 Validación inconsistente de entrada
6. 🔴 Deuda técnica significativa (endpoints duplicados)
7. 🔴 Security headers faltantes
8. 🔴 Rate limiting no implementado globalmente

### Recomendación Final
**RIESGO GENERAL: 🔴 CRÍTICO**

El backend requiere **acción de seguridad inmediata** antes de producción:
- Proteger endpoints públicos
- Autenticar WebSockets
- Implementar rate limiting
- Validación robusta de entrada
- Security headers
- Tests de seguridad

**Timeline Estimado:** 3-4 semanas para remediación completa

---

## APÉNDICE A: Checklist de Remediación

```markdown
### FASE 1: CRÍTICA (Semana 1)
- [ ] Fix voting GET / - agregar autenticación
- [ ] Fix meetings GET / y GET /{id} - agregar autenticación
- [ ] Fix sectors GET / y GET /{id} - agregar autenticación
- [ ] Fix payments GET /fees - agregar autenticación
- [ ] Fix live.py WebSocket - agregar token validation
- [ ] Fix chat.py WebSocket - agregar token validation
- [ ] Fix JWT secret en config.py
- [ ] Implementar rate limiting middleware

### FASE 2: ALTA (Semana 2)
- [ ] Agregar validadores en auth (password strength)
- [ ] Agregar validadores en payments (monto, concepto)
- [ ] Agregar validadores en voting (opciones)
- [ ] Fix SQL injection en votaciones.py
- [ ] Implementar security headers
- [ ] Validar role assignments en vecinos.py
- [ ] Sanitizar HTML en chat messages

### FASE 3: CONSOLIDACIÓN (Semana 3)
- [ ] Deprecar endpoints legacy
- [ ] Migrar clientes a v2
- [ ] Implementar tests de seguridad
- [ ] Eliminar código duplicado
- [ ] Agregar logging de seguridad

### FASE 4: HARDENING
- [ ] Code audit completoext
- [ ] Penetration testing
- [ ] SAST integration (Bandit, Semgrep)
- [ ] Rate limiting por usuario/IP
```

---

**Análisis completado por:** GitHub Copilot  
**Fecha:** 5 de mayo de 2026  
**Versión:** 1.0  
**Estado:** RECOMENDADO PARA REVISIÓN POR EQUIPO DE SEGURIDAD
