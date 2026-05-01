# Base de Datos - Archivos de Entrega

## Script Completo

Archivo principal:

```text
backend/supabase_schema.sql
```

Incluye:

- Tablas principales del sistema.
- Relaciones por llaves foraneas.
- Indices de busqueda y rendimiento.
- Vista `vista_morosos`.
- RPC `rpc_resultados_votacion`.
- RPC `rpc_resumen_financiero`.
- Configuracion de Realtime para tablas operativas.
- Tablas de documentos, pagos reales, comprobantes, noticias y votaciones.

## Backup

Script para crear backup desde PowerShell:

```text
backend/scripts/backup_supabase.ps1
```

Uso:

```powershell
cd backend
$env:DATABASE_URL="postgresql://postgres.ref:password@host:5432/postgres"
.\scripts\backup_supabase.ps1 -OutputPath .\backups\neighbord-backup.sql
```

Requisito: tener `pg_dump` instalado y disponible en `PATH`.

## Diagrama de Base de Datos

Archivo:

```text
docs/DIAGRAMA_BASE_DATOS.md
```

Contiene un diagrama Mermaid ERD con usuarios, reuniones, votaciones, pagos, documentos, noticias, directiva y relaciones.

## RPC

Funciones incluidas en `backend/supabase_schema.sql`:

```sql
select * from rpc_resultados_votacion('uuid-de-votacion');
select * from rpc_resumen_financiero();
```

## Realtime

Tablas agregadas a la publicacion `supabase_realtime`:

- `comunicados`
- `noticias`
- `votaciones`
- `votos`
- `pagos_cuotas`
- `documentos`

## Edge Function

Archivo de referencia:

```text
supabase/functions/send-email/index.ts
```

Despliegue:

```bash
supabase functions deploy send-email
supabase secrets set RESEND_API_KEY=tu_api_key
```

Esta funcion es una alternativa serverless para enviar correos desde Supabase usando Resend.
