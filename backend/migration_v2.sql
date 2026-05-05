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