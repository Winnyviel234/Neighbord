# Optimizaciones de Base de Datos para Supabase

## Índices Recomendados

Ejecuta estas queries en Supabase para crear índices que aceleren las búsquedas:

### Para tabla `usuarios` (Acelera login y búsquedas)
```sql
-- Índice en email (usado en login)
CREATE INDEX idx_usuarios_email ON usuarios(email);

-- Índice en sector_id (para filtros por sector)
CREATE INDEX idx_usuarios_sector_id ON usuarios(sector_id);

-- Índice en estado (para filtros de usuarios aprobados)
CREATE INDEX idx_usuarios_estado ON usuarios(estado);

-- Índice compuesto para búsquedas frecuentes
CREATE INDEX idx_usuarios_estado_activo ON usuarios(estado, activo);
```

### Para tabla `transacciones` (Acelera reportes financieros)
```sql
CREATE INDEX idx_transacciones_fecha ON transacciones(fecha);
CREATE INDEX idx_transacciones_usuario_id ON transacciones(usuario_id);
CREATE INDEX idx_transacciones_tipo ON transacciones(tipo);
```

### Para tabla `solicitudes` (Acelera búsquedas de reportes)
```sql
CREATE INDEX idx_solicitudes_estado ON solicitudes(estado);
CREATE INDEX idx_solicitudes_usuario_id ON solicitudes(usuario_id);
CREATE INDEX idx_solicitudes_created_at ON solicitudes(created_at);
```

### Para tabla `reuniones` (Acelera actas y cronogramas)
```sql
CREATE INDEX idx_reuniones_fecha ON reuniones(fecha);
CREATE INDEX idx_reuniones_estado ON reuniones(estado);
```

## Pasos para aplicar los índices

1. Ve a **Supabase Console** → **SQL Editor**
2. Copia y ejecuta cada query anterior
3. Verifica que los índices se crearon en **Table Editor** → elige tabla → pestaña **Indexes**

---

## Configuración de Redis (Caché)

Si tienes Redis disponible, agrega esta variable al `.env`:

```
REDIS_URL=redis://<usuario>:<password>@<host>:<puerto>/<database>
# Ejemplo local:
# REDIS_URL=redis://localhost:6379/0
```

El caché está habilitado automáticamente si esta variable existe.

---

## Optimizaciones Adicionales (Próximas fases)

### 1. Paginación en endpoints de listado
- Ya implementado en reportes con parámetro `limit`
- Falta agregar en otros endpoints (usuarios, transacciones, etc.)

### 2. Lazy loading del frontend
- Implementar infinite scroll o paginación en listados
- Cargar datos bajo demanda en lugar de todo de una vez

### 3. Compresión de imágenes
- Ya está en supabase.py (_compress_image)
- Se ejecuta automáticamente al subir imágenes

### 4. Cachés específicas por módulo
- Usar el decorator `@cache_response(ttl=600)` en endpoints que lee datos que cambian poco
- Ejemplo: listado de sectores, roles, configuraciones
