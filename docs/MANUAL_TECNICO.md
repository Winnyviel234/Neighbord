# Manual Técnico

## Arquitectura

El sistema usa React como SPA, FastAPI como API REST y Supabase como base PostgreSQL administrada.

## Backend

- `app/main.py`: instancia FastAPI y routers.
- `app/core/config.py`: variables de entorno.
- `app/core/security.py`: JWT, bcrypt y roles.
- `app/core/supabase.py`: cliente Supabase.
- `app/api/endpoints`: módulos REST.
- `app/services`: correos y reportes.

## Frontend

- `src/App.jsx`: rutas públicas y protegidas.
- `src/context/AuthContext.jsx`: sesión global.
- `src/services/api.js`: cliente Axios.
- `src/pages`: pantallas del sistema.
- `src/styles/globals.css`: Tailwind y estilos base.

## Variables obligatorias

Backend:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
JWT_SECRET_KEY=
```

Frontend:

```env
VITE_API_URL=http://localhost:8000/api
```

## Correos

SMTP Gmail requiere contraseña de aplicación:

```env
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
```

