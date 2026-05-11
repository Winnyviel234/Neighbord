# Neighbord API v2.0 - Documentación Técnica Fase 3

## Resumen Fase 3

Implementación de módulos mejorados para Pagos, Reuniones, Votaciones y Notificaciones con arquitectura completamente modular y RBAC.

## Módulos Implementados

### 1. Payments Module (`/api/v2/payments`)

**Responsabilidad:** Gestión de pagos y cuotas comunitarias

**Modelos:**
- `Payment`: Registro de pago individual
- `Fee`: Cuota comunitaria
- `PaymentVerify`: Verificación por tesorero/admin

**Endpoints:**

```bash
# Obtener mis pagos
GET /api/v2/payments
- Parámetro: estado (pendiente, verificado, rechazado)
- Respuesta: Lista de pagos del usuario

# Obtener todos los pagos (admin/tesorero/directiva)
GET /api/v2/payments/all
- Admin/tesorero pueden ver todos los pagos
- Respuesta: Lista filtrada

# Crear pago
POST /api/v2/payments
{
  "concepto": "Cuota mensual",
  "monto": 50000,
  "fecha_pago": "2026-05-04",
  "metodo": "transferencia",
  "referencia": "Ref123"
}

# Verificar pago (admin/tesorero)
PATCH /api/v2/payments/{id}/verify
{
  "estado": "verificado",
  "comprobante_url": "https://..."
}

# Obtener cuotas activas
GET /api/v2/payments/fees

# Ver estado de cuota para usuario
GET /api/v2/payments/fees/{fee_id}/status
```

**Permisos:**
- Vecino: Ver sus propios pagos, crear pagos
- Admin/Tesorero/Directiva: Ver todos los pagos, verificar
- Admin: Crear cuotas

---

### 2. Meetings Module (`/api/v2/meetings`)

**Responsabilidad:** Gestión de reuniones y asistencias

**Modelos:**
- `Meeting`: Información de reunión
- `Attendance`: Registro de asistencia
- Tipos: general, directiva

**Endpoints:**

```bash
# Listar reuniones
GET /api/v2/meetings?tipo=general&estado=programada
- Parámetros: tipo, estado
- Respuesta: Reuniones con contador de asistentes

# Ver reunión específica
GET /api/v2/meetings/{id}

# Crear reunión (admin/directiva)
POST /api/v2/meetings
{
  "titulo": "Asamblea General",
  "descripcion": "Discusión de presupuesto",
  "fecha": "2026-05-15T19:00:00Z",
  "lugar": "Salón comunitario",
  "tipo": "general"
}

# Actualizar reunión (admin/directiva)
PATCH /api/v2/meetings/{id}
{
  "estado": "activa"
}

# Eliminar reunión (admin)
DELETE /api/v2/meetings/{id}

# Registrar asistencia
POST /api/v2/meetings/{id}/attend
- Usuario registra su asistencia

# Ver asistentes
GET /api/v2/meetings/{id}/attendances
```

**Permisos:**
- Vecino: Ver reuniones, registrar asistencia
- Admin/Directiva: Crear, editar, eliminar reuniones
- Admin: Eliminar reuniones

---

### 3. Voting Module (`/api/v2/voting`)

**Responsabilidad:** Gestión de votaciones y votos

**Modelos:**
- `Voting`: Votación con múltiples opciones
- `Vote`: Voto individual
- Estados: activa, finalizada, cancelada

**Endpoints:**

```bash
# Listar votaciones
GET /api/v2/voting?estado=activa
- Respuesta: Con resultados y estadísticas

# Ver votación específica
GET /api/v2/voting/{id}
- Respuesta incluye: ya_voto, resultados, total_votos

# Crear votación (admin/directiva)
POST /api/v2/voting
{
  "titulo": "¿Aumento de cuota?",
  "descripcion": "Votación sobre aumento mensual",
  "fecha_inicio": "2026-05-04T18:00:00Z",
  "fecha_fin": "2026-05-11T23:59:59Z",
  "opciones": ["Sí", "No", "Abstención"]
}

# Votar
POST /api/v2/voting/{id}/vote?opcion=Sí
- Solo si votación está activa
- Una votación por usuario
- No se puede cambiar el voto

# Cerrar votación (admin)
PATCH /api/v2/voting/{id}/close
```

**Permisos:**
- Vecino: Ver votaciones, votar (una vez)
- Admin/Directiva: Crear votaciones
- Admin: Cerrar votaciones

**Características:**
- Prevent double voting (constraint unique)
- Resultados en tiempo real
- Indicador "ya_voto" para cada usuario

---

### 4. Notifications Module (`/api/v2/notifications`)

**Responsabilidad:** Sistema centralizado de notificaciones

**Modelos:**
- `Notification`: Notificación individual
- Tipos: info, warning, error, success
- Referencia a objetos relacionados (complaint, meeting, etc)

**Endpoints:**

```bash
# Obtener notificaciones
GET /api/v2/notifications?unread_only=true
- Parámetro: unread_only (true/false)
- Ordenado por fecha descendente

# Contar no leídas
GET /api/v2/notifications/unread/count
- Respuesta: {"unread_count": 5}

# Ver notificación específica
GET /api/v2/notifications/{id}
- Solo propietario o admin

# Marcar como leída
PATCH /api/v2/notifications/{id}/read

# Marcar múltiples como leídas
POST /api/v2/notifications/mark-multiple-read
{
  "ids": ["uuid1", "uuid2", "uuid3"]
}

# Eliminar notificación
DELETE /api/v2/notifications/{id}
```

**Tipos de Notificación:**
- info: Información general
- warning: Advertencia
- error: Error
- success: Confirmación de acción

**Integración:**
Se crean automáticamente cuando:
- Nueva queja asignada a admin
- Comentario en queja asignada
- Nueva reunión programada
- Votación creada
- Pago verificado/rechazado

---

## Flujo de Autorización RBAC

```
Middleware Validator
    ↓
get_current_user (verifica JWT)
    ↓
require_permissions(*permisos) O require_roles(*roles)
    ↓
Service (valida reglas de negocio)
    ↓
Repository (acceso a BD)
```

**Roles y Permisos:**

| Rol | Permisos |
|-----|----------|
| admin | all |
| directiva | manage_users, manage_meetings, manage_voting, manage_finances, view_reports |
| tesorero | manage_finances, view_reports |
| vecino | view_public, submit_complaints, vote |

---

## Manejo de Errores

Todos los endpoints retornan códigos HTTP estándar:

```
200: OK
201: Created
400: Bad Request (validación)
401: Unauthorized (sin autenticación)
403: Forbidden (sin permisos)
404: Not Found
409: Conflict (recurso duplicado, votación cerrada, etc)
500: Server Error
```

Formato de error:
```json
{
  "detail": "Descripción del error"
}
```

---

## Migración de BD Fase 3

Ejecutar `migration_v2.sql` que incluye:
1. Tablas nuevas (complaint_comments, etc)
2. Columnas adicionales (assigned_to, updated_at, etc)
3. Índices de rendimiento
4. Valores por defecto

---

## Próximas Fases

**Fase 4:** Integración con sistemas externos
- API Strike para pagos reales
- Google Maps para geolocalización
- WhatsApp para notificaciones

**Fase 5:** Reportes avanzados
- Dashboard con estadísticas
- Exportación de datos
- Auditoría detallada

**Fase 6:** Optimizaciones
- Caching con Redis
- Búsqueda con Elasticsearch
- Monitoreo y alertas