# Manual Técnico

## 1. Visión general

Neighbor es una aplicación web de gestión comunitaria construida con una arquitectura cliente-servidor. El frontend es una SPA en React/Vite, el backend es una API REST en FastAPI y la persistencia principal se realiza sobre Supabase/PostgreSQL. El sistema cubre autenticación, usuarios, vecinos, reuniones, votaciones, solicitudes, comunicados, noticias, pagos, finanzas, reportes, notificaciones y módulos administrativos.

La plataforma separa responsabilidades de forma sencilla:

- `frontend`: experiencia de usuario, rutas, formularios, consumo de API y estado de sesión.
- `backend`: reglas de negocio, autenticación, autorización, integración con Supabase, correos y reportes.
- `supabase`: base de datos PostgreSQL administrada y almacenamiento relacionado.
- `docs`: documentación funcional, técnica y de entrega.

La regla de seguridad más importante del flujo de acceso es que una cuenta en estado `pendiente` no debe recibir sesión utilizable ni acceder al dashboard. El registro crea al usuario como pendiente; el login y las rutas protegidas solo permiten estados `aprobado` o `activo`.

## 2. Estructura del repositorio

```text
community-system2/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/        # Endpoints legacy y funcionales
│   │   ├── core/                 # Configuración, seguridad y Supabase
│   │   ├── modules/              # Módulos modernos por dominio
│   │   ├── schemas/              # Modelos de entrada/salida compartidos
│   │   └── services/             # Servicios de correo, reportes y notificaciones
│   ├── scripts/                  # Utilidades de setup y verificación
│   ├── tests o test_*.py         # Pruebas y scripts de diagnóstico
│   └── supabase_schema.sql       # Esquema base de PostgreSQL
├── frontend/
│   ├── src/
│   │   ├── components/           # Componentes visuales reutilizables
│   │   ├── context/              # AuthContext y estado global
│   │   ├── hooks/                # Hooks auxiliares
│   │   ├── pages/                # Pantallas de la aplicación
│   │   ├── services/             # Cliente Axios y datos demo
│   │   └── lib/                  # Utilidades
│   └── vite.config.js
├── docs/
└── README.md
```

## 3. Stack tecnológico

### 3.1 Frontend

- React.
- Vite.
- React Router.
- Axios.
- Tailwind CSS o clases utilitarias equivalentes.
- Componentes comunes para layout, badges, spinners y manejo de errores.

### 3.2 Backend

- Python.
- FastAPI.
- Pydantic.
- Supabase Python client.
- Passlib/bcrypt para contraseñas.
- python-jose para JWT.
- Servicios propios para correo, reportes y notificaciones.

### 3.3 Base de datos

- PostgreSQL administrado por Supabase.
- Tablas principales: `usuarios`, `roles`, `sectors`, `reuniones`, `votaciones`, `votos`, `pagos`, `pagos_cuotas`, `transacciones`, `solicitudes`, `comunicados`, `noticias`, `documentos`, `audit_logs` y tablas auxiliares.

## 4. Configuración de entorno

### 4.1 Backend

Variables críticas:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Variables de correo:

```env
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

Variables opcionales:

```env
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
REDIS_URL=
```

`JWT_SECRET_KEY` debe ser fuerte, privado y diferente por ambiente. No debe subirse al repositorio.

### 4.2 Frontend

```env
VITE_API_URL=http://localhost:8000/api
```

El frontend consume rutas como `/api/v2/auth/login`, construidas a partir de la base configurada.

## 5. Instalación local

### 5.1 Backend

Pasos típicos:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si no existe `requirements.txt` o el proyecto usa otro archivo de dependencias, revisa el README principal.

### 5.2 Frontend

```powershell
cd frontend
npm install
npm run dev
```

La URL habitual de Vite es `http://localhost:5173`, salvo que el puerto esté ocupado.

## 6. Arquitectura del backend

`backend/app/main.py` crea la aplicación FastAPI, configura CORS y registra routers. Hay dos estilos de rutas:

- Rutas modernas en `app/modules/*`, montadas normalmente bajo `/api/v2`.
- Rutas legacy o funcionales en `app/api/endpoints/*`, montadas bajo `/api`.

La autenticación moderna está en:

- `app/modules/auth/model.py`: esquemas de registro, login y perfil.
- `app/modules/auth/repository.py`: acceso a tabla `usuarios`.
- `app/modules/auth/service.py`: reglas de negocio.
- `app/modules/auth/routes.py`: endpoints `/auth/register`, `/auth/login`, `/auth/me`.
- `app/core/security.py`: JWT, hashing, usuario actual y permisos.

## 7. Flujo de autenticación

### 7.1 Registro

Endpoint:

```text
POST /api/v2/auth/register
```

El backend:

1. Valida el payload.
2. Busca si el correo ya existe.
3. Hashea la contraseña con bcrypt.
4. Crea un registro en `usuarios`.
5. Define `estado = pendiente`.
6. Define `activo = true`.
7. Envía correo de bienvenida si está configurado.
8. Devuelve mensaje y usuario sin `password_hash`.

Por seguridad, el registro no debe devolver `access_token`. Una cuenta pendiente no debe iniciar sesión automáticamente.

### 7.2 Login

Endpoint:

```text
POST /api/v2/auth/login
```

El backend:

1. Busca el usuario por correo.
2. Verifica contraseña con bcrypt.
3. Rechaza credenciales inválidas con `401`.
4. Rechaza usuarios no aprobados con `403`.
5. Genera JWT solo si `estado` es `aprobado` o `activo`.
6. Devuelve token y usuario sin hash.

### 7.3 Usuario actual

Endpoint:

```text
GET /api/v2/auth/me
```

Usa `get_current_user`. Este dependency:

1. Decodifica JWT.
2. Obtiene `sub`.
3. Busca usuario en Supabase.
4. Verifica que exista.
5. Verifica `activo`.
6. Verifica `estado` aprobado/activo.
7. Adjunta rol, permisos y sector.

Si el usuario está pendiente, incluso con un token viejo, debe recibir `403`.

## 8. Autorización y roles

El sistema usa roles como:

- `admin`.
- `directiva`.
- `tesorero`.
- `vecino`.

La función `require_permissions` permite proteger endpoints por permiso. En frontend, `Protected` restringe rutas por rol y estado.

La autorización debe aplicarse en backend aunque exista control visual en frontend. El frontend mejora experiencia; el backend protege datos reales.

## 9. Control de cuentas pendientes

El control correcto tiene varias capas:

1. `register`: crea cuenta pendiente sin token.
2. `login`: no genera token si el estado no está aprobado.
3. `get_current_user`: rechaza tokens de usuarios pendientes.
4. `get_optional_current_user`: trata pendientes como usuario anónimo.
5. `AuthContext`: no guarda token tras registro.
6. `Protected`: no renderiza `/app` si el usuario no está aprobado.
7. `RegisterPage`: muestra mensaje de espera y no navega al dashboard.

Este diseño evita bypass por redirección, token antiguo, estado local o manipulación manual del navegador.

## 10. Arquitectura del frontend

El frontend tiene rutas públicas y privadas:

- Públicas: landing, login, registro, noticias públicas.
- Privadas: `/app` y sus subrutas.
- Privadas por rol: vecinos, finanzas, directiva, reportes, admin dashboard.

`src/App.jsx` define rutas y usa el componente `Protected`.

`src/context/AuthContext.jsx` centraliza:

- Usuario actual.
- Estado de carga.
- Login.
- Registro.
- Actualización de perfil.
- Cambio de contraseña.
- Logout.
- Validación de rol.

`src/services/api.js` centraliza Axios, interceptores, endpoints y fallback demo para algunas vistas.

## 11. Cliente API

El cliente Axios debe:

- Usar `VITE_API_URL`.
- Adjuntar `Authorization: Bearer <token>` cuando exista.
- Limpiar sesión ante `401` si corresponde.
- Propagar mensajes de error del backend.

Endpoints principales de autenticación:

```javascript
authService.login(data)
authService.register(data)
authService.me()
authService.updateMe(data)
authService.changePassword(data)
```

Servicios de datos:

```javascript
dataService.dashboard()
dataService.aprobarVecino(id)
dataService.getStatistics('dashboard')
```

## 12. Base de datos

La tabla `usuarios` es central. Campos típicos:

- `id`.
- `nombre`.
- `email`.
- `password_hash`.
- `telefono`.
- `direccion`.
- `documento`.
- `rol`.
- `role_id`.
- `sector_id`.
- `estado`.
- `activo`.
- `created_at`.

El esquema define estados permitidos:

```sql
estado text not null default 'pendiente'
check (estado in ('pendiente','aprobado','activo','inactivo','rechazado','moroso'))
```

Índices recomendados:

```sql
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);
CREATE INDEX idx_usuarios_sector_id ON usuarios(sector_id);
CREATE INDEX idx_usuarios_estado_activo ON usuarios(estado, activo);
```

## 13. Aprobación de usuarios

El módulo administrativo de vecinos permite aprobar usuarios. En frontend aparece en `VecinosPage.jsx`. El servicio asociado llama un endpoint como:

```text
PATCH /api/vecinos/{id}/aprobar
```

El endpoint debe:

1. Verificar que el actor tenga rol permitido.
2. Buscar el usuario objetivo.
3. Cambiar `estado` a `aprobado`.
4. Mantener auditoría si está disponible.
5. Devolver el usuario actualizado.

Nunca debe aprobar automáticamente desde registro.

## 14. Seguridad

### 14.1 Contraseñas

- Nunca guardar contraseñas en texto plano.
- Usar bcrypt mediante `hash_password`.
- Verificar con `verify_password`.
- Evitar logs con contraseñas o tokens.

### 14.2 JWT

- Incluir `sub`, `role` y `sector_id` cuando aplique.
- Firmar con `JWT_SECRET_KEY`.
- Definir expiración.
- Rechazar tokens inválidos, expirados o sin usuario.

### 14.3 Datos personales

El sistema maneja nombres, correos, teléfonos y direcciones. Por eso:

- No exponer listados completos a usuarios sin permiso.
- No devolver `password_hash`.
- No compartir dumps de base de datos sin sanitizar.
- Restringir reportes con datos sensibles.

### 14.4 CORS

Permitir solo orígenes necesarios en producción. En desarrollo puede abrirse a localhost.

### 14.5 Service role

`SUPABASE_SERVICE_ROLE_KEY` tiene privilegios altos. Debe existir solo en backend y nunca en frontend.

## 15. Módulos funcionales

### 15.1 Dashboard

Resume datos de pagos, solicitudes, reuniones y votaciones. Debe paginar o limitar consultas si crece el volumen.

### 15.2 Vecinos

Gestiona padrón, estados, aprobación y edición básica. Es un módulo sensible por datos personales.

### 15.3 Reuniones

Administra convocatorias, asistencia y seguimiento.

### 15.4 Votaciones

Debe garantizar una votación por usuario cuando aplique. La base debe tener restricción única por `votacion_id` y `usuario_id`.

### 15.5 Solicitudes

Permite crear y seguir casos comunitarios. Debe respetar propiedad: un vecino no debe editar solicitudes ajenas salvo permiso.

### 15.6 Pagos y finanzas

Controlan cuotas, comprobantes, ingresos, egresos y balances. Requieren permisos estrictos y auditoría.

### 15.7 Comunicados y noticias

Separan avisos oficiales de publicaciones informativas. La edición debe limitarse a roles autorizados.

### 15.8 Reportes

Generan PDF, CSV o resúmenes. Deben validar permisos y evitar exportaciones masivas no controladas.

## 16. Manejo de errores

Convenciones recomendadas:

| Código | Uso |
|---|---|
| 400 | Datos inválidos o regla de negocio incumplida |
| 401 | No autenticado o token inválido |
| 403 | Autenticado sin permiso o cuenta pendiente |
| 404 | Recurso no encontrado |
| 409 | Conflicto, por ejemplo correo duplicado |
| 500 | Error inesperado |

Los mensajes deben ser claros para el usuario, pero no revelar detalles sensibles.

## 17. Pruebas recomendadas

### 17.1 Autenticación

Casos mínimos:

- Registro crea usuario pendiente.
- Registro no devuelve token.
- Login con cuenta pendiente devuelve `403`.
- Login con cuenta aprobada devuelve token.
- `/auth/me` con token válido aprobado devuelve usuario.
- `/auth/me` con usuario pendiente devuelve `403`.
- Token inválido devuelve `401`.

### 17.2 Frontend

Casos mínimos:

- Registro muestra mensaje de espera.
- Registro no navega a `/app`.
- Login pendiente muestra error.
- Login aprobado entra al dashboard.
- Ruta `/app` sin usuario redirige a login.
- Ruta administrativa sin rol redirige.

### 17.3 Módulos

- Vecinos: aprobación y edición.
- Solicitudes: creación, listado y cambio de estado.
- Pagos: creación, verificación y rechazo.
- Votaciones: voto único.
- Reportes: exportación con permisos.

## 18. Comandos útiles

Backend:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
python pre_presentation_check.py
python test_login.py
```

Frontend:

```powershell
cd frontend
npm run dev
npm run build
```

Búsqueda rápida:

```powershell
rg "get_current_user" backend
rg "Protected" frontend/src
rg "pendiente" .
```

## 19. Despliegue

### 19.1 Backend

En producción:

- Usar servidor ASGI como Uvicorn/Gunicorn.
- Configurar variables por entorno.
- Activar HTTPS en el proxy o plataforma.
- Restringir CORS.
- Revisar logs.
- No usar claves de desarrollo.

### 19.2 Frontend

Construir con:

```powershell
npm run build
```

Publicar el contenido de `dist/` en el hosting elegido. `VITE_API_URL` debe apuntar al backend real.

### 19.3 Supabase

Antes de producción:

- Aplicar esquema.
- Crear índices.
- Revisar políticas RLS si se usan clientes directos.
- Crear usuario administrador inicial.
- Probar conexión desde backend.

## 20. Operación y mantenimiento

Tareas periódicas:

- Revisar cuentas pendientes.
- Revisar errores de backend.
- Verificar expiración de credenciales SMTP.
- Validar backups.
- Auditar roles administrativos.
- Archivar reportes antiguos si el volumen crece.
- Revisar tablas grandes e índices.
- Probar login después de cambios de seguridad.

## 21. Auditoría

Se recomienda registrar:

- Aprobación de usuarios.
- Cambios de rol.
- Cambios financieros.
- Verificación o rechazo de pagos.
- Eliminaciones.
- Exportación de reportes sensibles.

Un log útil debe incluir:

- Usuario actor.
- Acción.
- Tabla o módulo.
- Registro afectado.
- Fecha.
- Cambios antes/después cuando aplique.
- IP y user agent si están disponibles.

## 22. Rendimiento

Áreas a vigilar:

- Dashboard con consultas múltiples.
- Reportes grandes.
- Listados de vecinos sin paginación.
- Búsquedas sin índices.
- Exportaciones financieras.

Buenas prácticas:

- Agregar `limit` y paginación.
- Indexar campos usados en filtros.
- Evitar traer columnas innecesarias.
- Cachear datos de lectura frecuente cuando sea seguro.
- No ejecutar reportes pesados en cada render.

## 23. Compatibilidad y codificación

El proyecto contiene textos en español. Los archivos deben guardarse en UTF-8. Si aparecen caracteres corruptos como `sesiÃ³n`, revisar la codificación del editor y normalizar a UTF-8.

Para evitar inconsistencias:

- Usar un editor configurado en UTF-8.
- Evitar mezclar codificaciones.
- Revisar textos visibles antes de presentar.

## 24. Checklist de seguridad antes de entregar

- Registro no devuelve token.
- Cuenta pendiente no entra al dashboard.
- Login pendiente devuelve `403`.
- `/auth/me` valida estado.
- Frontend limpia token después de registro.
- `password_hash` no se devuelve.
- `JWT_SECRET_KEY` no está hardcodeado.
- `SUPABASE_SERVICE_ROLE_KEY` no existe en frontend.
- Rutas administrativas validan rol.
- Reportes sensibles requieren permiso.
- CORS está restringido en producción.

## 25. Solución de problemas

### 25.1 El usuario pendiente entra al dashboard

Revisar:

- Si `register` devuelve `access_token`.
- Si `AuthContext.register` guarda token.
- Si `Protected` valida estado.
- Si `/auth/me` acepta usuarios pendientes.
- Si hay token viejo en `localStorage`.

### 25.2 Login siempre falla

Revisar:

- URL de API.
- Conexión a Supabase.
- Hash de contraseña.
- Estado de usuario.
- Variables JWT.
- Logs de backend.

### 25.3 El frontend no conecta

Revisar:

- `VITE_API_URL`.
- CORS.
- Backend levantado.
- Puerto correcto.
- Consola del navegador.

### 25.4 Supabase no responde

Revisar:

- `SUPABASE_URL`.
- `SUPABASE_SERVICE_ROLE_KEY`.
- Red.
- Permisos de la tabla.
- Nombre de tabla o columnas.

### 25.5 Correos no salen

Revisar:

- Usuario SMTP.
- Contraseña de aplicación.
- Puerto.
- TLS.
- Cuenta bloqueada por proveedor.

## 26. Guía para nuevos desarrolladores

1. Lee `README.md`.
2. Levanta backend.
3. Levanta frontend.
4. Revisa `AuthContext.jsx`.
5. Revisa `app/core/security.py`.
6. Crea usuario de prueba pendiente.
7. Comprueba que no pueda entrar.
8. Aprueba usuario desde módulo de vecinos o base.
9. Comprueba acceso.
10. Ejecuta build del frontend.

Este recorrido enseña el flujo completo y detecta la mayoría de errores de configuración.

## 27. Convenciones de desarrollo

- Mantener reglas de negocio en backend.
- Mantener validaciones de experiencia en frontend.
- No duplicar secretos.
- No exponer hashes.
- Preferir servicios/repositories existentes.
- Evitar cambios globales sin prueba.
- Documentar cambios de seguridad.
- Probar roles después de tocar rutas.

## 28. Resumen técnico del flujo crítico

El sistema debe comportarse así:

```text
Usuario se registra
  -> backend crea usuario estado=pendiente
  -> backend responde sin token
  -> frontend muestra mensaje de espera
  -> frontend no navega a /app

Usuario pendiente intenta login
  -> backend valida contraseña
  -> backend detecta estado pendiente
  -> backend responde 403
  -> frontend muestra error

Administrador aprueba
  -> estado cambia a aprobado

Usuario aprobado inicia sesión
  -> backend crea JWT
  -> frontend guarda token
  -> Protected permite /app
```

Mientras esa secuencia se mantenga, el sistema conserva el control administrativo de acceso.

## 29. Arquitectura lógica por capas

La aplicación se entiende mejor si se divide en capas:

| Capa | Responsabilidad | Ejemplos |
|---|---|---|
| Presentación | Renderizar pantallas, formularios, navegación y estados visuales | React, páginas, componentes |
| Estado de cliente | Mantener sesión, usuario, carga y errores | `AuthContext` |
| Cliente API | Centralizar llamadas HTTP, sanitizar payloads y adjuntar token | `services/api.js` |
| Rutas backend | Exponer endpoints REST y declarar dependencias | `routes.py`, `endpoints/*.py` |
| Servicios backend | Aplicar reglas de negocio | `AuthService`, `StatisticsService` |
| Repositorios | Acceder a Supabase y aislar consultas | `repository.py` |
| Seguridad | JWT, roles, permisos y usuario actual | `core/security.py` |
| Persistencia | Tablas, índices, restricciones y vistas | Supabase/PostgreSQL |

Esta separación reduce acoplamiento y facilita mantenimiento. Un cambio de UI no debería alterar reglas de negocio; un cambio de base no debería duplicarse en múltiples pantallas.

## 30. Contratos principales de API

### 30.1 Registro

Solicitud:

```json
{
  "nombre": "Nombre completo",
  "email": "correo@dominio.com",
  "password": "contraseña",
  "telefono": "+59170000000",
  "direccion": "Calle y número",
  "sector": "Sector A"
}
```

Respuesta esperada:

```json
{
  "message": "Registro creado. Espera aprobación de la directiva.",
  "status": "pending_approval",
  "user": {
    "id": "uuid",
    "nombre": "Nombre completo",
    "email": "correo@dominio.com",
    "estado": "pendiente"
  }
}
```

No debe incluir `access_token`.

### 30.2 Login

Solicitud:

```json
{
  "email": "correo@dominio.com",
  "password": "contraseña"
}
```

Respuesta para usuario aprobado:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "correo@dominio.com",
    "estado": "aprobado",
    "rol": "vecino"
  }
}
```

Respuesta para usuario pendiente:

```json
{
  "detail": "Tu cuenta aún no está aprobada"
}
```

Código HTTP recomendado: `403`.

### 30.3 Dashboard administrativo

Endpoint:

```text
GET /api/v2/statistics/dashboard
```

Estructura esperada:

```json
{
  "users": {
    "total_users": 0,
    "active_users_30d": 0,
    "users_by_role": {},
    "users_by_status": {}
  },
  "payments": {
    "total_payments": 0,
    "total_amount": 0,
    "payments_by_status": {},
    "payments_by_method": {},
    "recent_payments_30d": 0
  },
  "votings": {
    "total_votings": 0,
    "active_votings": 0,
    "total_votes": 0,
    "recent_votings_30d": 0
  },
  "meetings": {
    "total_meetings": 0,
    "upcoming_meetings": 0,
    "past_meetings": 0
  },
  "complaints": {
    "total_complaints": 0,
    "complaints_by_status": {},
    "complaints_by_category": {},
    "recent_complaints_30d": 0
  },
  "chat": {
    "total_chat_rooms": 0,
    "total_messages": 0,
    "recent_messages_7d": 0
  },
  "generated_at": "2026-05-08T00:00:00"
}
```

El frontend debe tolerar campos faltantes para evitar pantallas rotas durante migraciones.

## 31. Panel administrativo

El panel administrativo debe funcionar como centro de control, no como una simple lista de contadores. Debe responder preguntas operativas:

- ¿Cuántos vecinos están esperando aprobación?
- ¿Cuántos pagos necesitan verificación?
- ¿Cuántas solicitudes siguen abiertas?
- ¿Cuál es el estado general de la comunidad?
- ¿Hay votaciones o reuniones activas?
- ¿Qué módulos requieren atención inmediata?

### 31.1 Componentes recomendados

- Cabecera ejecutiva con estado del sistema y fecha de corte.
- KPIs principales.
- Cola de trabajo prioritaria.
- Salud operativa.
- Distribución por estados y roles.
- Finanzas y pagos.
- Agenda y participación.
- Acciones rápidas.

### 31.2 Métricas calculadas en frontend

Algunas métricas pueden derivarse del payload:

```text
tasa_aprobacion = usuarios_aprobados / total_usuarios
tasa_recaudacion = pagos_verificados / total_pagos
tasa_resolucion = solicitudes_resueltas / total_solicitudes
pendientes_criticos = cuentas_pendientes + pagos_pendientes + solicitudes_abiertas
```

Estas métricas no sustituyen auditoría financiera; sirven como lectura ejecutiva.

### 31.3 Reglas de diseño del panel

- Mostrar primero lo accionable.
- Usar colores para prioridad, no para decorar.
- No depender de una sola métrica.
- Evitar tablas largas en la primera vista.
- Mantener enlaces directos a módulos operativos.
- Mostrar fecha de generación de datos.
- Permitir actualización manual.

## 32. Modelo de permisos recomendado

### 32.1 Backend

Todo endpoint sensible debe depender de:

```python
Depends(get_current_user)
```

Y cuando aplique:

```python
Depends(require_roles("admin", "directiva", "tesorero"))
```

O:

```python
Depends(require_permissions("users.manage"))
```

El control de frontend no es suficiente. Cualquier usuario puede intentar llamar endpoints manualmente.

### 32.2 Frontend

El frontend debe:

- Ocultar rutas sin permiso.
- Redirigir si el usuario no está autenticado.
- Redirigir si la cuenta no está aprobada.
- Evitar guardar tokens de registros pendientes.
- Mostrar errores claros.

### 32.3 Estados bloqueantes

Estos estados no deben entrar a `/app`:

- `pendiente`.
- `rechazado`.
- `inactivo`.
- Usuario inexistente.
- Usuario con `activo = false`.

## 33. Auditoría técnica

La auditoría debe capturar acciones que afectan confianza o trazabilidad.

Eventos recomendados:

- Registro de usuario.
- Aprobación de cuenta.
- Rechazo de cuenta.
- Cambio de rol.
- Cambio de estado de usuario.
- Login exitoso.
- Intento de acceso rechazado por estado.
- Creación de pago.
- Verificación de pago.
- Rechazo de pago.
- Creación de transacción financiera.
- Exportación de reporte.
- Publicación de comunicado.
- Eliminación de contenido.

Estructura sugerida:

```json
{
  "usuario_id": "uuid",
  "accion": "users.approve",
  "tabla": "usuarios",
  "registro_id": "uuid",
  "cambios_antes": {},
  "cambios_despues": {},
  "ip_address": "0.0.0.0",
  "user_agent": "browser",
  "created_at": "timestamp"
}
```

## 34. Estrategia de pruebas

### 34.1 Unitarias

Cubren funciones puras y servicios:

- Validación de estados.
- Cálculo de métricas.
- Normalización de usuarios.
- Sanitización de payloads.
- Reglas de permisos.

### 34.2 Integración

Cubren API + base:

- Registro crea usuario.
- Login aprobado genera token.
- Login pendiente devuelve `403`.
- Estadísticas responden para admin.
- Estadísticas rechazan vecino.
- Aprobar usuario cambia estado.

### 34.3 End to end

Cubren flujos del navegador:

- Usuario se registra y queda en pantalla de espera.
- Usuario pendiente intenta login y falla.
- Admin aprueba usuario.
- Usuario aprobado entra al dashboard.
- Admin abre panel administrativo.
- Admin navega a cuentas pendientes.

## 35. Plan de respaldo y recuperación

### 35.1 Respaldo

Se recomienda:

- Backup diario de base de datos.
- Backup antes de migraciones.
- Exportación periódica de reportes críticos.
- Respaldo de documentos subidos.
- Registro seguro de variables de entorno.

### 35.2 Recuperación

Procedimiento:

1. Identificar el incidente.
2. Detener cambios si hay riesgo de corrupción.
3. Revisar logs.
4. Confirmar último backup válido.
5. Restaurar en ambiente de prueba si es posible.
6. Validar usuarios, pagos y documentos.
7. Restaurar producción.
8. Documentar causa y acciones preventivas.

## 36. Gestión de migraciones

Antes de aplicar una migración:

- Revisar SQL.
- Confirmar backup.
- Probar en ambiente no productivo.
- Verificar índices.
- Revisar permisos/RLS si aplica.
- Preparar rollback lógico.

Después de aplicar:

- Probar login.
- Probar panel admin.
- Probar registro.
- Probar reportes.
- Revisar logs.

## 37. Observabilidad

El sistema debe registrar suficiente información para diagnosticar errores:

- Errores HTTP.
- Tiempo de respuesta de endpoints críticos.
- Fallos de Supabase.
- Fallos de SMTP.
- Errores de generación de reportes.
- Accesos rechazados por permisos.
- Conteo de usuarios pendientes.

En producción conviene integrar un sistema de logs centralizado.

## 38. Rendimiento del panel administrativo

El panel administrativo concentra varias métricas. Para evitar lentitud:

- Cachear estadísticas por 1 a 3 minutos.
- Evitar consultas `select("*")` si solo se necesita conteo.
- Usar índices por `estado`, `rol`, `created_at` y `sector_id`.
- Calcular agregados en SQL cuando el volumen crezca.
- Paginación para tablas de detalle.
- No refrescar automáticamente cada pocos segundos sin necesidad.

## 39. Checklist de release

Antes de entregar una versión:

- Build frontend exitoso.
- Backend arranca sin errores de importación.
- Login funciona.
- Registro pendiente no entra.
- Admin puede aprobar.
- Panel admin carga.
- Reportes descargan.
- No hay secretos en repositorio.
- Variables de entorno documentadas.
- Migraciones aplicadas.
- Manuales actualizados.

## 40. Checklist de revisión de seguridad

- Contraseñas hasheadas.
- JWT firmado con secreto fuerte.
- Tokens no se emiten a pendientes.
- `/me` valida estado.
- Endpoints administrativos requieren rol.
- Reportes sensibles requieren rol.
- Service role solo en backend.
- CORS restringido.
- Logs sin contraseñas.
- Payloads sanitizados.
- Archivos subidos validados.

## 41. Glosario técnico

- `SPA`: aplicación de una sola página.
- `JWT`: token firmado para autenticación.
- `Dependency`: función FastAPI que se ejecuta antes del endpoint.
- `Repository`: capa de acceso a datos.
- `Service`: capa de reglas de negocio.
- `Payload`: datos enviados por el cliente.
- `RLS`: Row Level Security en PostgreSQL/Supabase.
- `KPI`: indicador clave de rendimiento.
- `Cache`: almacenamiento temporal para acelerar consultas.
- `Build`: versión compilada del frontend.

## 42. Cierre técnico

La estabilidad del sistema depende de conservar tres principios: reglas críticas en backend, experiencia clara en frontend y base de datos con restricciones coherentes. El control de cuentas pendientes es un ejemplo de ese enfoque: se valida en registro, login, usuario actual, rutas protegidas y navegación. Esa defensa por capas debe mantenerse para cualquier flujo sensible que se agregue en el futuro.
