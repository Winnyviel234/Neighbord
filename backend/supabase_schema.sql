create extension if not exists "pgcrypto";

create table if not exists usuarios (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  email text unique not null,
  password_hash text not null,
  telefono text,
  direccion text,
  documento text,
  rol text not null default 'vecino' check (rol in ('admin','directiva','tesorero','vecino')),
  estado text not null default 'pendiente' check (estado in ('pendiente','aprobado','activo','inactivo','rechazado','moroso')),
  activo boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists reuniones (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  descripcion text,
  fecha timestamptz not null,
  lugar text not null,
  tipo text not null default 'general' check (tipo in ('general','directiva')),
  estado text not null default 'programada',
  creado_por uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists asistencias (
  id uuid primary key default gen_random_uuid(),
  reunion_id uuid not null references reuniones(id) on delete cascade,
  usuario_id uuid not null references usuarios(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (reunion_id, usuario_id)
);

create table if not exists votaciones (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  descripcion text,
  fecha_inicio timestamptz not null,
  fecha_fin timestamptz not null,
  opciones jsonb not null default '[]'::jsonb,
  estado text not null default 'activa',
  creado_por uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists votos (
  id uuid primary key default gen_random_uuid(),
  votacion_id uuid not null references votaciones(id) on delete cascade,
  usuario_id uuid not null references usuarios(id) on delete cascade,
  opcion text not null,
  created_at timestamptz not null default now(),
  unique (votacion_id, usuario_id)
);

create table if not exists pagos (
  id uuid primary key default gen_random_uuid(),
  vecino_id uuid not null references usuarios(id),
  concepto text not null,
  monto numeric(12,2) not null check (monto >= 0),
  fecha_pago date not null,
  metodo text not null default 'efectivo',
  referencia text,
  estado text not null default 'pendiente' check (estado in ('pendiente','verificado','rechazado')),
  comprobante_url text,
  verificado_por uuid references usuarios(id),
  verificado_at timestamptz,
  registrado_por uuid references usuarios(id),
  -- Strike integration fields
  strike_invoice_id text,
  strike_payment_request text,
  strike_lnurl text,
  strike_expires_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists transacciones (
  id uuid primary key default gen_random_uuid(),
  tipo text not null check (tipo in ('ingreso','egreso')),
  categoria text not null,
  descripcion text not null,
  monto numeric(12,2) not null check (monto >= 0),
  fecha date not null,
  registrado_por uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists solicitudes (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id),
  titulo text not null,
  descripcion text not null,
  categoria text not null default 'general',
  prioridad text not null default 'media',
  estado text not null default 'abierta',
  created_at timestamptz not null default now()
);

create table if not exists comunicados (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  contenido text not null,
  categoria text not null default 'general',
  publicado boolean not null default true,
  autor_id uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists noticias (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  resumen text not null,
  contenido text not null,
  imagen_url text,
  publicado boolean not null default true,
  autor_id uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists proyectos (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  descripcion text,
  estado text not null default 'planificado',
  presupuesto numeric(12,2) default 0,
  fecha_inicio date,
  fecha_fin date,
  created_at timestamptz not null default now()
);

create table if not exists auditoria (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid references usuarios(id),
  accion text not null,
  detalle jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists directiva (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid references usuarios(id),
  nombre text not null,
  email text,
  telefono text,
  cargo text not null check (cargo in ('presidente','vice_presidente','secretario','tesorero','vocal')),
  periodo text not null,
  activo boolean not null default true,
  created_at timestamptz not null default now()
);

alter table reuniones add column if not exists imagen_url text;
alter table votaciones add column if not exists imagen_url text;
alter table directiva add column if not exists imagen_url text;
alter table noticias add column if not exists imagen_url text;

create table if not exists documentos (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  descripcion text,
  archivo_url text not null,
  nombre_archivo text,
  tipo text,
  subido_por uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists cuotas (
  id uuid primary key default gen_random_uuid(),
  titulo text not null,
  descripcion text,
  monto numeric(12,2) not null check (monto >= 0),
  fecha_vencimiento date not null,
  estado text not null default 'activa' check (estado in ('activa','cerrada','cancelada')),
  creado_por uuid references usuarios(id),
  created_at timestamptz not null default now()
);

create table if not exists pagos_cuotas (
  id uuid primary key default gen_random_uuid(),
  cuota_id uuid not null references cuotas(id) on delete cascade,
  vecino_id uuid not null references usuarios(id),
  monto numeric(12,2) not null check (monto >= 0),
  fecha_pago date not null default current_date,
  metodo text not null default 'efectivo',
  referencia text,
  registrado_por uuid references usuarios(id),
  created_at timestamptz not null default now(),
  unique (cuota_id, vecino_id)
);

alter table pagos_cuotas add column if not exists estado text not null default 'pendiente' check (estado in ('pendiente','verificado','rechazado'));
alter table pagos_cuotas add column if not exists comprobante_url text;
alter table pagos_cuotas add column if not exists verificado_por uuid references usuarios(id);
alter table pagos_cuotas add column if not exists verificado_at timestamptz;

create or replace view vista_morosos as
select
  u.id,
  u.nombre,
  u.email,
  u.telefono,
  u.direccion,
  coalesce(sum(p.monto), 0) as total_pagado,
  case when u.estado = 'moroso' then 1 else 0 end as cuotas_pendientes
from usuarios u
left join pagos p on p.vecino_id = u.id
where u.rol = 'vecino'
group by u.id;

create index if not exists idx_usuarios_email on usuarios(email);
create index if not exists idx_reuniones_fecha on reuniones(fecha);
create index if not exists idx_solicitudes_usuario on solicitudes(usuario_id);
create index if not exists idx_pagos_vecino on pagos(vecino_id);
create index if not exists idx_directiva_cargo on directiva(cargo);
create index if not exists idx_cuotas_estado on cuotas(estado);
create index if not exists idx_votos_votacion on votos(votacion_id);
create index if not exists idx_pagos_cuotas_cuota on pagos_cuotas(cuota_id);
create index if not exists idx_pagos_cuotas_vecino on pagos_cuotas(vecino_id);
create index if not exists idx_pagos_cuotas_estado on pagos_cuotas(estado);
create index if not exists idx_documentos_created_at on documentos(created_at desc);
create index if not exists idx_noticias_publicado on noticias(publicado, created_at desc);

delete from comunicados a
using comunicados b
where a.id > b.id
  and a.titulo = b.titulo
  and a.contenido = b.contenido;

create unique index if not exists idx_comunicados_unicos on comunicados(titulo, contenido);

create or replace function rpc_resultados_votacion(p_votacion_id uuid)
returns table(opcion text, votos bigint, porcentaje numeric)
language sql
stable
as $$
  with total as (
    select count(*)::numeric as total_votos
    from votos
    where votacion_id = p_votacion_id
  )
  select
    opcion,
    count(*) as votos,
    case when (select total_votos from total) = 0 then 0
      else round((count(*)::numeric / (select total_votos from total)) * 100, 2)
    end as porcentaje
  from votos
  where votacion_id = p_votacion_id
  group by opcion;
$$;

create or replace function rpc_resumen_financiero()
returns table(total_ingresos numeric, total_egresos numeric, balance numeric, pagos_pendientes bigint)
language sql
stable
as $$
  select
    coalesce(sum(case when tipo = 'ingreso' then monto else 0 end), 0) as total_ingresos,
    coalesce(sum(case when tipo = 'egreso' then monto else 0 end), 0) as total_egresos,
    coalesce(sum(case when tipo = 'ingreso' then monto else -monto end), 0) as balance,
    (select count(*) from pagos_cuotas where estado = 'pendiente') as pagos_pendientes
  from transacciones;
$$;

do $$
begin
  alter publication supabase_realtime add table comunicados;
exception when duplicate_object then null;
end $$;

do $$
begin
  alter publication supabase_realtime add table noticias;
exception when duplicate_object then null;
end $$;

do $$
begin
  alter publication supabase_realtime add table votaciones;
exception when duplicate_object then null;
end $$;

do $$
begin
  alter publication supabase_realtime add table votos;
exception when duplicate_object then null;
end $$;

do $$
begin
  alter publication supabase_realtime add table pagos_cuotas;
exception when duplicate_object then null;
end $$;

do $$
begin
  alter publication supabase_realtime add table documentos;
exception when duplicate_object then null;
end $$;

-- Usuario inicial: cambia el password desde la app después de configurar un hash real.
-- Para crear admin usa /api/auth/register y luego:
-- update usuarios set rol='admin', estado='aprobado' where email='tu-correo@gmail.com';
