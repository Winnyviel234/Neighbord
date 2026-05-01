# Neighbord

## Nombre del Proyecto

**Neighbord - Sistema de Gestion Comunitaria**

## Descripcion del Proyecto

Neighbord es una plataforma web para administrar una junta de vecinos o comunidad residencial. Permite gestionar residentes, directiva, reuniones, votaciones, pagos reales con comprobantes, comunicados, noticias, documentos, reportes, mapa del sector y correos institucionales.

El sistema esta dividido en un frontend React y un backend FastAPI conectado a Supabase para base de datos, almacenamiento y funciones de apoyo.

## Tecnologias Utilizadas

- Frontend: React, Vite, JavaScript, Tailwind CSS, React Router, Axios, Lucide React.
- Backend: Python, FastAPI, Uvicorn, Pydantic, Python-Jose, Passlib.
- Base de datos: Supabase PostgreSQL.
- Archivos: Supabase Storage y respaldo local en `backend/uploads`.
- Correos: SMTP Gmail con clave de aplicacion.
- Reportes: ReportLab para PDF y CSV compatible con Excel.
- Realtime: Supabase Realtime y WebSocket interno del backend.
- Edge Function: Supabase Edge Function de referencia en `supabase/functions/send-email`.

## Caracteristicas del Sistema

- Autenticacion con JWT.
- Roles: administrador, directiva, tesorero y vecino.
- Registro de vecinos y aprobacion administrativa.
- Gestion de reuniones generales e internas de directiva.
- Votaciones reales con registro unico por usuario y estadisticas.
- Elecciones con asignacion de roles.
- Pagos reales de cuotas con comprobante, estado pendiente/verificado/rechazado.
- Gestion financiera de ingresos, egresos, cuotas y reportes.
- Comunicados y noticias con imagenes.
- Subida y consulta de documentos.
- Fotos de perfil para miembros de directiva.
- Correos personalizados con nombre y logo de Neighbord.
- Mapa del sector con ubicacion configurable.
- Reportes PDF y CSV.

## Requisitos del Sistema

- Windows 10/11 o sistema compatible.
- Python 3.10 o superior.
- Node.js 18 o superior.
- npm.
- Cuenta Supabase.
- Cuenta Gmail con verificacion en dos pasos y clave de aplicacion.
- `pg_dump` si se desea generar backup de base de datos.

## Instalacion del Proyecto

### Clone de Repositorio de GitHub

```bash
git clone https://github.com/tu-usuario/neighbord.git
cd neighbord
```

Si el proyecto ya esta en la computadora, entra directamente a la carpeta:

```bash
cd community-system2
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

## Configuracion

### Backend `.env`

Variables principales:

```env
APP_NAME=Neighbord Community System
FRONTEND_URL=http://localhost:5173
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
DATABASE_URL=postgresql://postgres.ref:password@host:5432/postgres
JWT_SECRET_KEY=clave-segura
ADMIN_NAME=Administrador Neighbord
ADMIN_EMAIL=admin@correo.com
ADMIN_PASSWORD=clave-inicial
MAIL_USERNAME=tu-correo@gmail.com
MAIL_PASSWORD=claveaplicaciongmail
MAIL_FROM=tu-correo@gmail.com
MAIL_FROM_NAME=Neighbord
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

No publiques claves reales en GitHub.

### Base de Datos

Ejecuta el script completo:

```text
backend/supabase_schema.sql
```

Tambien puedes usar:

```bash
cd backend
.\.venv\Scripts\python.exe scripts\setup_supabase.py
```

## Paso de Ejecucion del Proyecto

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

### 3. Compilar Produccion

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
      context/
      pages/
      services/
      styles/
    package.json
  docs/
    BASE_DATOS_ENTREGA.md
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
