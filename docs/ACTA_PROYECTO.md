# Acta del Proyecto

## Proyecto

Neighbor - Sistema Comunitario para Junta de Vecinos.

## Alcance

Sistema web con autenticación, roles, padrón, reuniones, votaciones, solicitudes, comunicados, noticias, finanzas, reportes y correos.

## Tecnologías aprobadas

- React
- JavaScript
- FastAPI
- Supabase
- Gmail SMTP

## Exclusiones

- Docker
- TypeScript
- Angular

## Criterios de aceptación

- La aplicación corre localmente sin Docker.
- El frontend consume el backend mediante `VITE_API_URL`.
- El backend consume Supabase mediante variables `.env`.
- El envío de correo funciona al configurar credenciales SMTP válidas.

