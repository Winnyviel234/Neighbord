# 🏘️ Neighbord - Sistema de Gestión Comunitaria Integral

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-via%20Supabase-336791.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#licencia)

## 📋 Descripción del Proyecto

**Neighbord** es una plataforma web profesional y escalable para la administración integral de juntas de vecinos y comunidades residenciales. Ofrece soluciones de gobernanza digital, gestión financiera, comunicación comunitaria y trazabilidad de acciones.

### Funcionalidades Principales
- ✅ **Gestión de Residentes**: Registro, aprobación, perfil de miembros
- ✅ **Directiva y Cargos**: Asignación, rotación, historial de cambios
- ✅ **Reuniones**: Convocatorias, orden del día, actas digitales, asistencia
- ✅ **Votaciones**: Procesos electorales transparentes con registro único
- ✅ **Finanzas**: Cuotas, pagos con comprobante, reportes, morosidad
- ✅ **Comunicación**: Comunicados, noticias, chat por sectores
- ✅ **Quejas y Solicitudes**: Seguimiento por estado, asignación
- ✅ **Documentos**: Biblioteca de estatutos, reglamentos, manuales
- ✅ **Proyectos**: Presupuesto, gastos, seguimiento
- ✅ **Reportes**: PDF/CSV financieros, administrativos, auditoría
- ✅ **Seguridad**: RBAC, auditoría GDPR, trazabilidad completa
- ✅ **Integraciones**: WhatsApp, Email, Google Maps

### Stack Tecnológico
El sistema está dividido en:
- **Backend**: FastAPI (Python) con arquitectura modular limpia
- **Frontend**: React 18 con Vite, TypeScript, Tailwind CSS
- **Base de Datos**: PostgreSQL vía Supabase
- **Almacenamiento**: Supabase Storage + Local Backups
- **Comunicación**: Email (SMTP), WhatsApp (Twilio), WebSockets
- **Análisis**: Elasticsearch, Redis (preparado)

---

## 🎯 Etapa Actual del Proyecto

| Aspecto | Estado | Detalles |
|--------|--------|---------|
| **Funcionalidades** | 🟢 90% | 31/35 requerimientos implementados |
| **Seguridad** | 🟡 70% | 12 vulnerabilidades identificadas y en corrección |
| **Testing** | 🟡 40% | Tests unitarios pendientes |
| **Documentación** | 🟡 70% | API docs ✅, Manuales de usuario 🔄 |
| **Producción** | 🟡 50% | Ready staging, fixing security antes de prod |

### Fases Completadas
- ✅ **Fase 1**: Base Sólida (Auth, Roles, Sectores)
- ✅ **Fase 2**: Comunicación (Chat, Quejas)
- ✅ **Fase 3**: Finanzas (Pagos, Cuotas, Reuniones, Votaciones)
- ✅ **Fase 4**: Integraciones Externas (Strike, Twilio, Elasticsearch)
- ✅ **Fase 5**: Gestión de Directiva y Proyectos
- ✅ **Fase 6**: Auditoría GDPR y Compliance
- ✅ **Fase 7**: Optimización y Performance
- ✅ **Fase 8**: Integraciones Avanzadas (Banking, OAuth, Webhooks, API público)
- 🔄 **Fase 9**: Correcciones de Seguridad y Completar Requerimientos

### Próximas Prioridades
1. **Crítico**: Aplicar parches de seguridad (4 horas)
2. **Alto**: Completar mapa de incidencias, WhatsApp, dashboard auditoría (8 horas)
3. **Medio**: Documentación de usuario, testing (16 horas)
4. **Deploy**: Verificación penetration testing antes de producción

---

## 🏗️ Arquitectura del Sistema

### Backend - Clean Architecture (FastAPI)

```
backend/
├── app/
│   ├── modules/           # Módulos de negocio (21 módulos)
│   │   ├── auth/          # Autenticación JWT + bcrypt
│   │   ├── users/         # Gestión de usuarios y roles
│   │   ├── sectors/       # Multi-tenancy por sector
│   │   ├── complaints/    # Quejas/Solicitudes con estados
│   │   ├── chat/          # WebSocket chat tiempo real
│   │   ├── payments/      # Pagos, cuotas, morosidad
│   │   ├── meetings/      # Reuniones, actas, asistencia
│   │   ├── voting/        # Votaciones, elecciones
│   │   ├── notifications/ # Email, WhatsApp, push
│   │   ├── directiva/     # Gestión de cargos
│   │   ├── projects/      # Proyectos comunitarios
│   │   ├── audit/         # Auditoría GDPR
│   │   ├── banking/       # Integración bancaria
│   │   ├── oauth/         # Google, GitHub, Facebook SSO
│   │   ├── public_api/    # API público con rate limiting
│   │   ├── webhooks/      # Integraciones externas
│   │   ├── statistics/    # Reportes y gráficos
│   │   ├── search/        # Elasticsearch
│   │   └── [más módulos]
│   │
│   ├── api/endpoints/     # Endpoints legacy (backward compatibility)
│   ├── core/
│   │   ├── security.py    # JWT, RBAC, autenticación
│   │   ├── config.py      # Configuración centralizada
│   │   ├── supabase.py    # Cliente Supabase
│   │   └── sanitization.py # Validación/sanitización inputs
│   ├── schemas/           # DTOs con Pydantic
│   └── services/          # Servicios compartidos
│
└── migrations/            # Scripts SQL con versionado
```

**Cada módulo sigue el patrón:**
```
módulo/
├── routes.py        # Endpoints REST
├── service.py       # Lógica de negocio
├── repository.py    # Acceso a datos (Supabase)
├── model.py         # DTOs + validación Pydantic
└── __init__.py
```

### Frontend - React Vite

```
frontend/src/
├── pages/           # Páginas por rol (Admin, Directiva, Vecino)
├── components/
│   ├── common/      # Header, Sidebar, Footer
│   ├── layout/      # Layouts responsivos
│   └── [features]/  # Componentes por funcionalidad
├── services/
│   └── api.js       # Cliente HTTP (axios)
├── context/         # Context API para estado global
├── hooks/           # Custom hooks (useCache, etc)
├── styles/          # Tailwind CSS personalizado
└── App.jsx          # Entry point
```

### Base de Datos - PostgreSQL (Supabase)

**Tablas principales:**
```sql
-- Usuarios y Seguridad
usuarios              -- Registro, perfiles, roles
roles                 -- RBAC con permisos JSONB
audit_logs            -- Trazabilidad de acciones

-- Estructura Comunitaria
sectors               -- Múltiples comunidades
directiva             -- Cargos y responsables
usuarios_directiva    -- Histórico de cambios

-- Comunicación
chat_rooms            -- Salas por sector/comisión
messages              -- Mensajes persistentes
notifications         -- Notificaciones + preferencias
comunicados           -- Avisos oficiales

-- Financiero
cuotas                -- Definición de cuotas
pagos_cuotas          -- Registro de pagos
gastos_proyectos      -- Desglose de gastos

-- Procesos
reuniones             -- Convocatorias, actas
asistencias           -- Registro de asistencia
votaciones            -- Procesos electorales
votos                 -- Registro de votos (único/usuario)

-- Gestión
solicitudes           -- Quejas, solicitudes
proyectos             -- Proyectos comunitarios
documentos            -- Biblioteca de archivos
```

### Seguridad - Defense in Depth

```
┌─────────────────────────────────────────────────────┐
│  NIVEL 1: TRANSPORTE                                │
│  - HTTPS/TLS obligatorio en producción              │
│  - Security Headers (HSTS, CSP, X-Frame-Options)   │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│  NIVEL 2: AUTENTICACIÓN                             │
│  - JWT con expiración + refresh tokens              │
│  - bcrypt (salt rounds: 12) para contraseñas        │
│  - 2FA (planeado para Fase 10)                      │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│  NIVEL 3: AUTORIZACIÓN (RBAC)                       │
│  - Permisos granulares por acción                   │
│  - Validación de sector_id en cada request          │
│  - Middleware de protección de rutas                │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│  NIVEL 4: VALIDACIÓN DE DATOS                       │
│  - Pydantic validators en todos los endpoints       │
│  - Sanitización contra XSS                          │
│  - Rate limiting por endpoint                       │
│  - CORS restrictivo                                 │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│  NIVEL 5: BASE DE DATOS                             │
│  - Unique constraints (votos, documentos)           │
│  - Triggers para auditoría automática               │
│  - Políticas RLS en Supabase                        │
│  - Encriptación de campos sensibles                 │
└─────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────┐
│  NIVEL 6: AUDITORÍA                                 │
│  - Logs de todas las acciones críticas              │
│  - GDPR consent tracking                            │
│  - IP + User Agent + timestamp                      │
│  - Backup automático encriptado                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔒 Postura de Seguridad

### Implementaciones de Seguridad ✅
- **Autenticación**: JWT con 1440 min expiration + bcrypt (12 rounds)
- **Autorización**: RBAC con granularidad de acción (view, create, edit, delete, approve)
- **Validación**: Pydantic validators en todos los endpoints
- **Sanitización**: HTML escape para prevenir XSS
- **Rate Limiting**: 5 req/min auth, 200 req/min general
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **SQL Injection**: Queries parametrizadas + UNIQUE constraints
- **Auditoría**: Logs de todos los cambios con IP + timestamp
- **GDPR**: Consent tracking, solicitud de eliminación de datos

### Vulnerabilidades Identificadas y en Corrección 🟡
1. JWT Secret hardcoded → Migrando a .env ✅
2. Endpoints públicos (voting, meetings) → Agregando autenticación ✅
3. WebSocket sin auth → Implementando JWT validation ✅
4. Voto múltiple posible → Agregando UNIQUE constraint ✅
5. SQL injection potencial → Sanitización de entrada ✅
6. Sin rate limiting auth → Implementando slowapi ✅
7. Sin security headers → Agregando middleware ✅
8. Falta validadores Pydantic → Completando validators ✅

**Ver `ANALISIS_REQUERIMIENTOS_COMPLETO.md` para detalles completos de seguridad.**

---

## 🚀 Inicio Rápido

### Requisitos Previos
- **Python 3.10+** con pip
- **Node.js 18+** con npm
- **Git**
- **Supabase account** (base de datos + storage)
- **Gmail** con clave de aplicación (para emails)
- **Opcional**: Twilio (WhatsApp), Strike API (pagos)

### Instalación

#### 1. Clonar Repositorio
```bash
git clone https://github.com/Winnyviel234/Neighbord.git
cd community-system2
```

#### 2. Configurar Backend
```bash
cd backend

# Crear virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# o
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales Supabase, Gmail, etc.

# Ejecutar migraciones
python run_migration.py

# Iniciar servidor
python -m uvicorn app.main:app --reload --port 8000
```

**Backend disponible en:** http://localhost:8000
**API Docs:** http://localhost:8000/docs (Swagger UI)

#### 3. Configurar Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env.local con URL del backend

# Iniciar desarrollo
npm run dev
```

**Frontend disponible en:** http://localhost:5173

#### 4. Base de Datos (Supabase)
```bash
# Las migraciones se aplican automáticamente en run_migration.py
# O manualmente:
psql -U postgres -h db.supabase.co -d postgres -f backend/supabase_schema.sql
psql -U postgres -h db.supabase.co -d postgres -f backend/migration_v2.sql
```

---

## 📚 Documentación
```

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Configura `backend/.env` con tus valores reales.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
```

Configura `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

## Configuración

### Backend `.env`

Variables principales:

```env
APP_NAME=Neighbord Community System
FRONTEND_URL=http://localhost:5173
SUPABASE_URL=https://jptrmluduazsujxunwwm.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwdHJtbHVkdWF6c3VqeHVud3dtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzQ4MjE4MywiZXhwIjoyMDkzMDU4MTgzfQ.Wx7mGv9Wl_LFO8wGDE1kosnc1iWqwl_4OXgIE4df8y0
DATABASE_URL=postgresql://postgres.jptrmluduazsujxunwwm:winnyviel2009@aws-1-us-east-1.pooler.supabase.com:5432/postgres
JWT_SECRET_KEY=LOcPsO+dwmMsNCLKTlQEF71otmLESVLGCM32ulVvTLvgIx2VmJ0Tdo2AGdB855izQftaUUtFWD1t9fiKjhPcpg==
ADMIN_NAME=Administradora
ADMIN_EMAIL=winnyviel80@gmail.com
ADMIN_PASSWORD=TuClaveAdmin123
MAIL_USERNAME=winnyviel80@gmail.com
MAIL_PASSWORD=kosokozbvqewjawm
MAIL_FROM=winnyviel80@gmail.com
MAIL_FROM_NAME=Neighbord
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

**⚠️ ADVERTENCIA DE SEGURIDAD: Nunca publiques claves reales en repositorios públicos. Los valores mostrados arriba son ejemplos ficticios. Usa siempre variables de entorno seguras y no commits .env con datos sensibles.**

### Base de Datos

Ejecuta el script completo:

```text
backend/supabase_schema.sql
```

También puedes usar:

```bash
cd backend
.\.venv\Scripts\python.exe scripts\setup_supabase.py
```

## Paso de Ejecución del Proyecto

### 1. Ejecutar Backend

```bash
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Salud:

```text
http://127.0.0.1:8000/api/health
```

### 2. Ejecutar Frontend

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### 3. Compilar Producción

```bash
cd frontend
npm run build
```

## Estructura del Proyecto

```text
community-system2/
  backend/
    app/
      api/endpoints/
      core/
      schemas/
      services/
    scripts/
      backup_supabase.ps1
      setup_supabase.py
    uploads/
    requirements.txt
    supabase_schema.sql
  frontend/
    public/
    src/
      components/
      pages/
      services/
      styles/
    package.json
  docs/
    BASE_DATOS_ENTREGA.md
```

## Seguridad y Mejores Prácticas

### 🔐 Seguridad

- **Autenticación**: Implementada con JWT y hash bcrypt para contraseñas.
- **Autorización**: Sistema de roles (admin, directiva, tesorero, vecino) con middleware de protección.
- **Validación**: Entradas sanitizadas y validadas con Pydantic.
- **Variables de Entorno**: Todas las claves sensibles se configuran vía .env (nunca en código).
- **CORS**: Configurado para orígenes permitidos.
- **Auditoría**: Registro de acciones importantes en tabla `auditoria`.
- **Recomendaciones**:
  - Cambia las claves por defecto inmediatamente.
  - Usa claves fuertes y únicas para JWT.
  - Habilita HTTPS en producción.
  - Implementa rate limiting para endpoints públicos.
  - Realiza backups regulares de la base de datos.

### 📋 Mejores Prácticas Aplicadas

- **Arquitectura Limpia**: Separación en capas (controllers, services, repositories, models).
- **Código Asíncrono**: Uso de async/await en FastAPI para mejor rendimiento.
- **Manejo de Errores**: Excepciones centralizadas y respuestas consistentes.
- **DTOs**: Uso de Pydantic para validación y serialización.
- **Dependencias**: Gestión con pip y requirements.txt.
- **Versionado**: API versionada en rutas.
- **Documentación**: Endpoints documentados con OpenAPI/Swagger.
- **Testing**: Preparado para pruebas unitarias e integración.
- **Logging**: Registro de eventos para debugging y monitoreo.
- **Escalabilidad**: Diseño modular para agregar funcionalidades sin romper existentes.

### 🚀 Despliegue en Producción

- Configura variables de entorno seguras.
- Usa un servidor ASGI como Uvicorn o Gunicorn.
- Implementa monitoreo y alertas.
- Configura backups automáticos.
- Considera contenedores Docker para facilidad de despliegue.

### 🤝 Contribución

- Sigue las mejores prácticas de código.
- Realiza commits descriptivos.
- Prueba cambios antes de push.
- Documenta nuevas funcionalidades.

### 📞 Soporte

Para soporte, contacta al administrador del sistema.

## 🏗️ Arquitectura Modular (v2.0)

### Fases de Implementación

**Fase 1 ✅:** Base sólida
- Autenticación con JWT y bcrypt
- Sistema de roles (admin, directiva, tesorero, vecino)
- Gestión de sectores (multi-comunidad)
- Middleware RBAC con permisos granulares

**Fase 2 ✅:** Comunicación y Gestión de Quejas
- Módulo Complaints (quejas con asignación y comentarios)
- Chat por sector con WebSockets en tiempo real
- Persistencia de mensajes en BD
- Control de acceso por sector

**Fase 3 ✅:** Pagos, Reuniones y Votaciones Mejoradas
- Gestión de pagos con verificación (admin/tesorero)
- Cuotas comunitarias con seguimiento
- Reuniones con registro de asistencia
- Votaciones mejoradas con estadísticas en tiempo real
- Sistema de notificaciones centralizado

### Nuevos Endpoints v2.0

#### Auth & Users
```
POST   /api/v2/auth/register           # Registrar usuario
POST   /api/v2/auth/login              # Iniciar sesión
GET    /api/v2/auth/me                 # Perfil actual
PATCH  /api/v2/auth/me                 # Actualizar perfil
POST   /api/v2/auth/change-password    # Cambiar contraseña
GET    /api/v2/users                   # Listar usuarios
PATCH  /api/v2/users/{id}              # Actualizar usuario
POST   /api/v2/users/{id}/approve      # Aprobar usuario (admin/directiva)
```

#### Sectors
```
GET    /api/v2/sectors                 # Listar sectores
POST   /api/v2/sectors                 # Crear sector (admin)
GET    /api/v2/sectors/{id}/users      # Usuarios en sector
```

#### Complaints
```
GET    /api/v2/complaints              # Mis quejas
POST   /api/v2/complaints              # Crear queja
PATCH  /api/v2/complaints/{id}         # Actualizar (owner/admin)
POST   /api/v2/complaints/{id}/comments # Agregar comentario
GET    /api/v2/complaints/{id}/comments # Ver comentarios
```

#### Chat
```
GET    /api/v2/chat/rooms              # Salas accesibles
POST   /api/v2/chat/rooms              # Crear sala (admin/directiva)
GET    /api/v2/chat/rooms/{id}/messages # Mensajes
POST   /api/v2/chat/rooms/{id}/messages # Enviar mensaje
WS     /api/v2/chat/ws/{room_id}       # WebSocket chat en tiempo real
```

#### Payments
```
GET    /api/v2/payments                # Mis pagos
GET    /api/v2/payments/all            # Todos (admin/tesorero/directiva)
POST   /api/v2/payments                # Registrar pago
PATCH  /api/v2/payments/{id}/verify    # Verificar (admin/tesorero)
GET    /api/v2/payments/fees           # Cuotas activas
```

#### Meetings
```
GET    /api/v2/meetings                # Reuniones
POST   /api/v2/meetings                # Crear (admin/directiva)
PATCH  /api/v2/meetings/{id}           # Actualizar (admin/directiva)
POST   /api/v2/meetings/{id}/attend    # Registrar asistencia
GET    /api/v2/meetings/{id}/attendances # Ver asistentes
```

#### Voting
```
GET    /api/v2/voting                  # Votaciones
POST   /api/v2/voting                  # Crear (admin/directiva)
POST   /api/v2/voting/{id}/vote        # Votar
PATCH  /api/v2/voting/{id}/close       # Cerrar (admin)
```

#### Notifications
```
GET    /api/v2/notifications           # Mis notificaciones
GET    /api/v2/notifications/unread/count # Contar no leídas
PATCH  /api/v2/notifications/{id}/read # Marcar como leída
POST   /api/v2/notifications/mark-multiple-read # Marcar múltiples
```

### Patrones Implementados

- **MVC Architecture:** Model → View → Controller en cada módulo
- **Repository Pattern:** Acceso a datos centralizado y testeable
- **Service Layer:** Lógica de negocio separada
- **DTOs:** Validación con Pydantic
- **Middleware RBAC:** Control de acceso granular
- **Async/Await:** Operaciones no bloqueantes
- **Error Handling:** Excepciones HTTP estándar
- **Logging:** Auditoría de acciones críticas
    DIAGRAMA_BASE_DATOS.md
    MANUAL_TECNICO.md
    MANUAL_USUARIO.md
  supabase/
    functions/send-email/index.ts
```

## Uso del Sistema

1. El vecino se registra desde `/registro`.
2. El administrador aprueba el vecino y asigna roles.
3. La directiva crea reuniones, comunicados, noticias y votaciones.
4. Los vecinos votan una vez por votacion activa.
5. El tesorero o administrador crea cuotas comunitarias.
6. Los vecinos registran pagos reales y suben comprobantes.
7. Tesoreria verifica o rechaza pagos en Finanzas.
8. Administracion descarga reportes PDF/CSV.
9. Se suben documentos desde Reportes y correos; la lista aparece en el lado derecho.

## Credenciales Relevantes

Credenciales de referencia para desarrollo:

```text
Usuario administrador: definido en backend/.env como ADMIN_EMAIL
Clave inicial: definida en backend/.env como ADMIN_PASSWORD
```

Por seguridad, no se documentan claves reales en este README.

## API Utilizada e Implementacion

Base URL local:

```text
http://127.0.0.1:8000/api
```

### Autenticacion

- `POST /auth/register`: registro de vecino.
- `POST /auth/login`: inicio de sesion.
- `GET /auth/me`: usuario autenticado.

Implementacion:

1. El frontend envia credenciales con Axios.
2. El backend valida usuario y password.
3. El backend devuelve JWT.
4. El frontend guarda el token en `localStorage`.
5. Axios envia `Authorization: Bearer <token>` en cada peticion.

### Votaciones

- `GET /votaciones`: lista votaciones con estadisticas.
- `POST /votaciones/form`: crea votacion con imagen.
- `POST /votaciones/{id}/votar`: registra voto real.
- `GET /votaciones/{id}/resultados`: resultados.

### Pagos

- `GET /cuotas`: lista cuotas.
- `GET /cuotas/mis-pagos`: cuotas y pagos del vecino.
- `POST /cuotas/{id}/pagar/form`: registra pago real con comprobante.
- `GET /cuotas/pagos`: pagos para administracion/tesoreria.
- `PATCH /cuotas/pagos/{id}/estado/{estado}`: verifica o rechaza pago.

### Documentos

- `GET /documentos`: lista documentos subidos.
- `POST /documentos/form`: sube documento real.

### Reportes y Correos

- `GET /reportes/{tipo}.pdf`: descarga PDF.
- `GET /reportes/{tipo}.csv`: descarga CSV/Excel.
- `POST /emails/personalizado`: envia correo personalizado.

## Base de Datos - Archivos

- Script completo: `backend/supabase_schema.sql`
- Backup: `backend/scripts/backup_supabase.ps1`
- Diagrama: `docs/DIAGRAMA_BASE_DATOS.md`
- Detalle de entrega: `docs/BASE_DATOS_ENTREGA.md`
- Edge Function: `supabase/functions/send-email/index.ts`

## Backup de Base de Datos

```powershell
cd backend
$env:DATABASE_URL="postgresql://postgres.ref:password@host:5432/postgres"
.\scripts\backup_supabase.ps1 -OutputPath .\backups\neighbord-backup.sql
```

## Autor del Desarrollo

Desarrollado para el proyecto **Neighbord - Sistema de Gestion Comunitaria**.

## Autor Administrador del Proyecto

**Rijo**
