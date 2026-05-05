# Cronograma

| Fase | Actividades | Estado |
|---|---|---|
| 1 | Definición de requisitos | Completado |
| 2 | Diseño visual con logo Neighbor | Completado |
| 3 | Backend FastAPI y Supabase | Completado |
| 4 | Frontend React JS | Completado |
| 5 | Reportes y emails | Completado |
| 6 | Conexión real a Supabase del usuario | Completado |

## Pasos de despliegue

- Crear proyecto Supabase.
- Ejecutar SQL o usar `backend/scripts/setup_supabase.py`.
- Configurar `.env` con `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`.
- Crear contraseña de aplicación Gmail si se usa SMTP.
- Verificar conexión con `python backend/scripts/verify_supabase_connection.py`.

