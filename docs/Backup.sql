-- Archivo generado por Codex el 2026-05-12
-- Contiene todos los scripts SQL encontrados en backend/.



-- ============================================================
-- backend/supabase_schema.sql
-- ============================================================

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

-- Usuario inicial: cambia el password desde la app despuÃ©s de configurar un hash real.
-- Para crear admin usa /api/auth/register y luego:
-- update usuarios set rol='admin', estado='aprobado' where email='tu-correo@gmail.com';


-- ============================================================
-- backend/supabase_noticias.sql
-- ============================================================

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

create index if not exists idx_noticias_publicado on noticias(publicado, created_at desc);

delete from comunicados
where titulo in ('Asamblea comunitaria', 'Jornada de limpieza');

delete from noticias
where titulo in ('Nuevo sistema comunitario', 'ParticipaciÃ³n vecinal');


-- ============================================================
-- backend/migration_v2.sql
-- ============================================================

-- Migration script for Neighbord v2.0
-- Adds new tables and alters existing ones for modular architecture
-- Run after existing schema.sql

-- Create sectors table
CREATE TABLE IF NOT EXISTS sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Insert default roles
INSERT INTO roles (name, permissions) VALUES
('admin', '["all"]'::jsonb),
('directiva', '["manage_users", "manage_meetings", "manage_voting", "manage_finances", "view_reports"]'::jsonb),
('tesorero', '["manage_finances", "view_reports"]'::jsonb),
('vecino', '["view_public", "submit_complaints", "vote"]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Create chat_rooms table
CREATE TABLE IF NOT EXISTS chat_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID REFERENCES sectors(id),
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'sector' CHECK (type IN ('sector', 'commission')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',
    read BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Alter existing usuarios table
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS sector_id UUID REFERENCES sectors(id);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS role_id UUID REFERENCES roles(id);

-- Create default sector if none exists
INSERT INTO sectors (name, description) VALUES ('Comunidad Principal', 'Sector principal de la comunidad')
ON CONFLICT (name) DO NOTHING;

-- Update existing users to have default role 'vecino' and default sector
UPDATE usuarios SET role_id = (SELECT id FROM roles WHERE name = 'vecino') WHERE role_id IS NULL;
UPDATE usuarios SET sector_id = (SELECT id FROM sectors LIMIT 1) WHERE sector_id IS NULL;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_usuarios_sector ON usuarios(sector_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_role ON usuarios(role_id);
CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);

-- Create complaint_comments table
CREATE TABLE IF NOT EXISTS complaint_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    complaint_id UUID NOT NULL REFERENCES solicitudes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES usuarios(id),
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add new columns to existing solicitudes table
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES usuarios(id);
ALTER TABLE solicitudes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_complaint_comments_complaint ON complaint_comments(complaint_id);
CREATE INDEX IF NOT EXISTS idx_solicitudes_assigned ON solicitudes(assigned_to);
CREATE INDEX IF NOT EXISTS idx_solicitudes_status ON solicitudes(estado);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, read);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos(estado);
CREATE INDEX IF NOT EXISTS idx_pagos_vecino ON pagos(vecino_id);
CREATE INDEX IF NOT EXISTS idx_reuniones_tipo ON reuniones(tipo);
CREATE INDEX IF NOT EXISTS idx_reuniones_estado ON reuniones(estado);
CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado);
CREATE INDEX IF NOT EXISTS idx_votos_votacion ON votos(votacion_id);

-- ============================================================
-- backend/migration_notifications.sql
-- ============================================================

-- Tabla de notificaciones del sistema
CREATE TABLE IF NOT EXISTS public.notificaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    tipo VARCHAR(50), -- votacion, reunion, pago, solicitud, comunicado, directiva, chat
    referencia_id UUID,
    referencia_tipo VARCHAR(50), -- votacion, reunion, pago, solicitud, comunicado
    leida BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE
);

-- Ãndices para consultas frecuentes
CREATE INDEX idx_notificaciones_usuario_id ON public.notificaciones(usuario_id);
CREATE INDEX idx_notificaciones_leida ON public.notificaciones(leida);
CREATE INDEX idx_notificaciones_tipo ON public.notificaciones(tipo);
CREATE INDEX idx_notificaciones_created_at ON public.notificaciones(created_at DESC);

-- Tabla de preferencias de notificaciones por usuario
CREATE TABLE IF NOT EXISTS public.preferencias_notificaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE,
    -- Notificaciones en app
    votaciones BOOLEAN DEFAULT TRUE,
    reuniones BOOLEAN DEFAULT TRUE,
    pagos BOOLEAN DEFAULT TRUE,
    solicitudes BOOLEAN DEFAULT TRUE,
    comunicados BOOLEAN DEFAULT TRUE,
    directiva BOOLEAN DEFAULT FALSE,
    chat BOOLEAN DEFAULT FALSE,
    novedades BOOLEAN DEFAULT TRUE,
    -- Notificaciones por email
    email_votaciones BOOLEAN DEFAULT TRUE,
    email_reuniones BOOLEAN DEFAULT TRUE,
    email_pagos BOOLEAN DEFAULT TRUE,
    email_solicitudes BOOLEAN DEFAULT FALSE,
    email_comunicados BOOLEAN DEFAULT TRUE,
    email_directiva BOOLEAN DEFAULT FALSE,
    email_chat BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE
);

-- Ãndice para bÃºsqueda rÃ¡pida
CREATE INDEX idx_preferencias_notificaciones_usuario_id ON public.preferencias_notificaciones(usuario_id);
ALTER TABLE public.preferencias_notificaciones ADD COLUMN IF NOT EXISTS novedades BOOLEAN DEFAULT TRUE;

-- Trigger para actualizar updated_at en notificaciones
CREATE OR REPLACE FUNCTION update_notificaciones_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_notificaciones_updated_at ON public.notificaciones;
CREATE TRIGGER trigger_update_notificaciones_updated_at
BEFORE UPDATE ON public.notificaciones
FOR EACH ROW
EXECUTE FUNCTION update_notificaciones_updated_at();

-- Trigger para actualizar updated_at en preferencias
CREATE OR REPLACE FUNCTION update_preferencias_notificaciones_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_preferencias_notificaciones_updated_at ON public.preferencias_notificaciones;
CREATE TRIGGER trigger_update_preferencias_notificaciones_updated_at
BEFORE UPDATE ON public.preferencias_notificaciones
FOR EACH ROW
EXECUTE FUNCTION update_preferencias_notificaciones_updated_at();


-- ============================================================
-- backend/migration_password_reset.sql
-- ============================================================

-- Recuperacion segura de contrasenas
CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_hash ON public.password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_usuario ON public.password_reset_tokens(usuario_id);


-- ============================================================
-- backend/migration_strike_integration.sql
-- ============================================================

-- Migration: Add Strike integration fields to pagos table
-- Run this in Supabase SQL Editor or via migration script

-- Add new columns for Strike integration
ALTER TABLE pagos
ADD COLUMN IF NOT EXISTS estado text NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','verificado','rechazado')),
ADD COLUMN IF NOT EXISTS comprobante_url text,
ADD COLUMN IF NOT EXISTS verificado_por uuid REFERENCES usuarios(id),
ADD COLUMN IF NOT EXISTS verificado_at timestamptz,
ADD COLUMN IF NOT EXISTS strike_invoice_id text,
ADD COLUMN IF NOT EXISTS strike_payment_request text,
ADD COLUMN IF NOT EXISTS strike_lnurl text,
ADD COLUMN IF NOT EXISTS strike_expires_at timestamptz;

-- Create index for better performance on Strike queries
CREATE INDEX IF NOT EXISTS idx_pagos_strike_invoice_id ON pagos(strike_invoice_id);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos(estado);
CREATE INDEX IF NOT EXISTS idx_pagos_verificado_por ON pagos(verificado_por);

-- Update existing records to have 'verificado' status if they were previously verified
-- (This assumes existing payments were already verified)
UPDATE pagos
SET estado = 'verificado',
    verificado_at = created_at
WHERE estado IS NULL OR estado = 'pendiente';

-- ============================================================
-- backend/migration_phase7_audit.sql
-- ============================================================

-- Migration for Phase 7: Audit and Compliance
-- Adds audit logging table and GDPR compliance features

-- Create audit_logs table for detailed operation tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES usuarios(id),
    action TEXT NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, etc.
    resource_type TEXT NOT NULL, -- users, complaints, payments, etc.
    resource_id UUID, -- ID of the affected resource
    old_values JSONB, -- Previous state (for updates)
    new_values JSONB, -- New state
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB -- Additional context
);

-- Create indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- Create user_consents table for GDPR compliance
CREATE TABLE IF NOT EXISTS user_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    consent_type TEXT NOT NULL, -- marketing, data_processing, etc.
    consented BOOLEAN NOT NULL DEFAULT true,
    consent_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    withdrawal_date TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB
);

-- Create indexes for consents
CREATE INDEX IF NOT EXISTS idx_user_consents_user ON user_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_user_consents_type ON user_consents(consent_type);

-- Add GDPR fields to usuarios table
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS gdpr_consent_given BOOLEAN DEFAULT false;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS gdpr_consent_date TIMESTAMPTZ;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS data_retention_until DATE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS account_deletion_requested BOOLEAN DEFAULT false;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS account_deletion_date TIMESTAMPTZ;

-- Create data_deletion_requests table for GDPR right to be forgotten
CREATE TABLE IF NOT EXISTS data_deletion_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    request_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'completed', 'rejected')),
    processed_by UUID REFERENCES usuarios(id),
    processed_date TIMESTAMPTZ,
    notes TEXT
);

-- Create backup_logs table to track automated backups
CREATE TABLE IF NOT EXISTS backup_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type TEXT NOT NULL, -- full, incremental, config
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    file_path TEXT,
    file_size_bytes BIGINT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB
);

-- Insert default consents for existing users
INSERT INTO user_consents (user_id, consent_type, consented, consent_date)
SELECT
    u.id,
    'data_processing',
    true,
    now()
FROM usuarios u
WHERE NOT EXISTS (
    SELECT 1 FROM user_consents c
    WHERE c.user_id = u.id AND c.consent_type = 'data_processing'
);

-- Update existing roles with audit permissions
UPDATE roles SET permissions = '["all"]'::jsonb WHERE name = 'admin';
UPDATE roles SET permissions = '["manage_users", "manage_meetings", "manage_voting", "manage_finances", "view_reports", "view_audit_logs", "view_compliance"]'::jsonb WHERE name = 'directiva';
UPDATE roles SET permissions = '["manage_finances", "view_reports", "view_backups"]'::jsonb WHERE name = 'tesorero';
UPDATE roles SET permissions = '["view_public", "submit_complaints", "vote"]'::jsonb WHERE name = 'vecino';

-- ============================================================
-- backend/migration_phase9_banking.sql
-- ============================================================

-- Migration: Banking integration tables
-- Description: Creates tables for bank connections, accounts, transactions, and payments
-- Version: phase9_banking
-- Date: 2024

-- Bank connections table
CREATE TABLE IF NOT EXISTS bank_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    integration_id TEXT NOT NULL,
    external_id TEXT,
    status TEXT NOT NULL DEFAULT 'connected',
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- Bank accounts table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connection_id UUID REFERENCES bank_connections(id) ON DELETE CASCADE,
    bank_name TEXT NOT NULL,
    account_number TEXT NOT NULL, -- Masked for security
    account_type TEXT NOT NULL DEFAULT 'checking',
    currency TEXT NOT NULL DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sync TIMESTAMP WITH TIME ZONE,
    balance DECIMAL(15,2)
);

-- Bank transactions table
CREATE TABLE IF NOT EXISTS bank_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES bank_accounts(id) ON DELETE CASCADE,
    transaction_id TEXT NOT NULL, -- Bank's transaction ID
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    description TEXT NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_type TEXT NOT NULL, -- debit, credit
    category TEXT,
    merchant TEXT,
    reference TEXT,
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_data JSONB DEFAULT '{}',
    UNIQUE(account_id, transaction_id)
);

-- Payment initiations table
CREATE TABLE IF NOT EXISTS payment_initiations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    description TEXT NOT NULL,
    recipient_account TEXT NOT NULL,
    recipient_name TEXT NOT NULL,
    reference TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    external_transaction_id TEXT
);

-- Bank webhook events table
CREATE TABLE IF NOT EXISTS bank_webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    integration_id TEXT NOT NULL,
    connection_id TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bank_connections_user_id ON bank_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_connections_integration_id ON bank_connections(integration_id);
CREATE INDEX IF NOT EXISTS idx_bank_connections_status ON bank_connections(status);

CREATE INDEX IF NOT EXISTS idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_bank_accounts_connection_id ON bank_accounts(connection_id);
CREATE INDEX IF NOT EXISTS idx_bank_accounts_is_active ON bank_accounts(is_active);

CREATE INDEX IF NOT EXISTS idx_bank_transactions_account_id ON bank_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_transaction_date ON bank_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_transaction_type ON bank_transactions(transaction_type);

CREATE INDEX IF NOT EXISTS idx_payment_initiations_user_id ON payment_initiations(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_initiations_status ON payment_initiations(status);
CREATE INDEX IF NOT EXISTS idx_payment_initiations_created_at ON payment_initiations(created_at);

CREATE INDEX IF NOT EXISTS idx_bank_webhook_events_integration_id ON bank_webhook_events(integration_id);
CREATE INDEX IF NOT EXISTS idx_bank_webhook_events_connection_id ON bank_webhook_events(connection_id);
CREATE INDEX IF NOT EXISTS idx_bank_webhook_events_received_at ON bank_webhook_events(received_at);

-- RLS Policies (Row Level Security)
ALTER TABLE bank_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_initiations ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_webhook_events ENABLE ROW LEVEL SECURITY;

-- Bank connections: Users can only see their own
CREATE POLICY "Users can view their own bank connections" ON bank_connections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own bank connections" ON bank_connections
    FOR ALL USING (auth.uid() = user_id);

-- Bank accounts: Users can only see their own
CREATE POLICY "Users can view their own bank accounts" ON bank_accounts
    FOR SELECT USING (auth.uid() = user_id);

-- Bank transactions: Users can only see their own
CREATE POLICY "Users can view their own bank transactions" ON bank_transactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM bank_accounts ba
            WHERE ba.id = bank_transactions.account_id
            AND ba.user_id = auth.uid()
        )
    );

-- Payment initiations: Users can only see their own
CREATE POLICY "Users can view their own payment initiations" ON payment_initiations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own payment initiations" ON payment_initiations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Bank webhook events: Only admins can view
CREATE POLICY "Only admins can view bank webhook events" ON bank_webhook_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Comments for documentation
COMMENT ON TABLE bank_connections IS 'User connections to banking integrations';
COMMENT ON TABLE bank_accounts IS 'Bank accounts linked to user connections';
COMMENT ON TABLE bank_transactions IS 'Bank transactions imported from accounts';
COMMENT ON TABLE payment_initiations IS 'Payment initiation requests through banking';
COMMENT ON TABLE bank_webhook_events IS 'Webhook events received from banking providers';

COMMENT ON COLUMN bank_accounts.account_number IS 'Masked account number for security (e.g., ****1234)';
COMMENT ON COLUMN bank_transactions.transaction_id IS 'Unique transaction ID from the bank';
COMMENT ON COLUMN payment_initiations.external_transaction_id IS 'Transaction ID from payment processor';

-- ============================================================
-- backend/migration_phase9_oauth.sql
-- ============================================================

-- Migration: OAuth2/SSO tables
-- Description: Creates tables for OAuth account linking and external authentication
-- Version: phase9_oauth
-- Date: 2024

-- OAuth accounts table for linking external accounts
CREATE TABLE IF NOT EXISTS oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL, -- google, github, facebook, etc.
    provider_id TEXT NOT NULL,
    email TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, provider),
    UNIQUE(provider, provider_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_accounts_provider ON oauth_accounts(provider);
CREATE INDEX IF NOT EXISTS idx_oauth_accounts_provider_id ON oauth_accounts(provider_id);
CREATE INDEX IF NOT EXISTS idx_oauth_accounts_email ON oauth_accounts(email);

-- RLS Policies (Row Level Security)
ALTER TABLE oauth_accounts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own OAuth accounts
CREATE POLICY "Users can view their own OAuth accounts" ON oauth_accounts
    FOR SELECT USING (auth.uid() = user_id);

-- Users can manage their own OAuth accounts
CREATE POLICY "Users can manage their own OAuth accounts" ON oauth_accounts
    FOR ALL USING (auth.uid() = user_id);

-- Admins can view all OAuth accounts
CREATE POLICY "Admins can view all OAuth accounts" ON oauth_accounts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Function to create user from OAuth data
CREATE OR REPLACE FUNCTION create_user_from_oauth(
    p_email TEXT,
    p_name TEXT,
    p_provider TEXT,
    p_provider_id TEXT
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    new_user_id UUID;
    default_sector_id UUID;
BEGIN
    -- Get default sector (first one found)
    SELECT id INTO default_sector_id FROM sectors LIMIT 1;

    IF default_sector_id IS NULL THEN
        RAISE EXCEPTION 'No sectors available for user registration';
    END IF;

    -- Create new user
    INSERT INTO users (
        email,
        name,
        sector_id,
        created_at,
        updated_at,
        is_active
    ) VALUES (
        p_email,
        p_name,
        default_sector_id,
        NOW(),
        NOW(),
        true
    ) RETURNING id INTO new_user_id;

    -- Assign default role (regular user)
    INSERT INTO user_roles (user_id, role_id)
    SELECT new_user_id, id FROM roles WHERE name = 'user' LIMIT 1;

    RETURN new_user_id;
END;
$$;

-- Comments for documentation
COMMENT ON TABLE oauth_accounts IS 'Links user accounts to external OAuth providers';
COMMENT ON COLUMN oauth_accounts.provider IS 'OAuth provider name (google, github, facebook, etc.)';
COMMENT ON COLUMN oauth_accounts.provider_id IS 'Unique identifier from the OAuth provider';
COMMENT ON COLUMN oauth_accounts.access_token IS 'OAuth access token for API calls (optional)';

COMMENT ON FUNCTION create_user_from_oauth IS 'Creates a new user account from OAuth authentication data';

-- ============================================================
-- backend/migration_phase9_public_api.sql
-- ============================================================

-- Migration: Public API tables
-- Description: Creates tables for API key management and public data flags
-- Version: phase9_public_api
-- Date: 2024

-- API keys table for public API access
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    key TEXT UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    request_count INTEGER DEFAULT 0
);

-- Add public visibility flags to existing tables
ALTER TABLE projects ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(active);
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key);
CREATE INDEX IF NOT EXISTS idx_api_keys_expires_at ON api_keys(expires_at);

CREATE INDEX IF NOT EXISTS idx_projects_is_public ON projects(is_public);
CREATE INDEX IF NOT EXISTS idx_meetings_is_public ON meetings(is_public);
CREATE INDEX IF NOT EXISTS idx_complaints_is_public ON complaints(is_public);

-- RLS Policies (Row Level Security)
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Only admins can manage API keys
CREATE POLICY "API keys are manageable by admins only" ON api_keys
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Function to get public sectors with stats
CREATE OR REPLACE FUNCTION get_public_sectors()
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    location TEXT,
    total_users BIGINT,
    active_projects BIGINT,
    last_activity TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.description,
        s.location,
        COALESCE(user_counts.total_users, 0) as total_users,
        COALESCE(project_counts.active_projects, 0) as active_projects,
        GREATEST(
            s.created_at,
            COALESCE(user_counts.last_user_activity, s.created_at),
            COALESCE(project_counts.last_project_activity, s.created_at)
        ) as last_activity
    FROM sectors s
    LEFT JOIN (
        SELECT
            sector_id,
            COUNT(*) as total_users,
            MAX(created_at) as last_user_activity
        FROM users
        GROUP BY sector_id
    ) user_counts ON s.id = user_counts.sector_id
    LEFT JOIN (
        SELECT
            sector_id,
            COUNT(*) as active_projects,
            MAX(updated_at) as last_project_activity
        FROM projects
        WHERE status = 'active'
        GROUP BY sector_id
    ) project_counts ON s.id = project_counts.sector_id
    ORDER BY s.name;
END;
$$;

-- Comments for documentation
COMMENT ON TABLE api_keys IS 'Stores API keys for public API access with rate limiting';
COMMENT ON COLUMN api_keys.key IS 'The actual API key value used for authentication';
COMMENT ON COLUMN api_keys.request_count IS 'Number of requests made with this key';

COMMENT ON COLUMN projects.is_public IS 'Whether this project is visible in public API';
COMMENT ON COLUMN meetings.is_public IS 'Whether this meeting is visible in public API';
COMMENT ON COLUMN complaints.is_public IS 'Whether this complaint is visible in public API (limited fields)';

-- ============================================================
-- backend/migration_phase9_webhooks.sql
-- ============================================================

-- Migration: Webhook system tables
-- Description: Creates tables for webhook subscriptions, deliveries, and events
-- Version: phase9_webhooks
-- Date: 2024

-- Webhook subscriptions table
CREATE TABLE IF NOT EXISTS webhook_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    events JSONB NOT NULL DEFAULT '[]',
    secret TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_delivery TIMESTAMP WITH TIME ZONE,
    delivery_attempts INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

-- Webhook deliveries table (logs all delivery attempts)
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES webhook_subscriptions(id) ON DELETE CASCADE,
    event_id UUID NOT NULL,
    url TEXT NOT NULL,
    payload JSONB NOT NULL,
    status_code INTEGER,
    response_body TEXT,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    attempt_number INTEGER DEFAULT 1,
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhook events table (logs all triggered events)
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT DEFAULT 'neighbord'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_webhook_subscriptions_active ON webhook_subscriptions(active);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_subscription_id ON webhook_deliveries(subscription_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_success ON webhook_deliveries(success);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_delivered_at ON webhook_deliveries(delivered_at);
CREATE INDEX IF NOT EXISTS idx_webhook_events_event_type ON webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_resource_type ON webhook_events(resource_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_timestamp ON webhook_events(timestamp);

-- RLS Policies (Row Level Security)
ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_events ENABLE ROW LEVEL SECURITY;

-- Only admins can manage webhook subscriptions
CREATE POLICY "Webhook subscriptions are manageable by admins only" ON webhook_subscriptions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Webhook deliveries are read-only for admins
CREATE POLICY "Webhook deliveries are readable by admins only" ON webhook_deliveries
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Webhook events are read-only for admins
CREATE POLICY "Webhook events are readable by admins only" ON webhook_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = auth.uid() AND r.name = 'admin'
        )
    );

-- Insert policy for webhook deliveries (system can insert)
CREATE POLICY "System can insert webhook deliveries" ON webhook_deliveries
    FOR INSERT WITH CHECK (true);

-- Insert policy for webhook events (system can insert)
CREATE POLICY "System can insert webhook events" ON webhook_events
    FOR INSERT WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE webhook_subscriptions IS 'Stores webhook endpoint subscriptions for external integrations';
COMMENT ON TABLE webhook_deliveries IS 'Logs all webhook delivery attempts with status and responses';
COMMENT ON TABLE webhook_events IS 'Logs all webhook events that were triggered in the system';

COMMENT ON COLUMN webhook_subscriptions.events IS 'JSON array of event types this subscription listens to';
COMMENT ON COLUMN webhook_subscriptions.secret IS 'Secret key used to sign webhook payloads';
COMMENT ON COLUMN webhook_deliveries.payload IS 'The full JSON payload that was sent to the webhook endpoint';
COMMENT ON COLUMN webhook_events.data IS 'Additional data associated with the event';
