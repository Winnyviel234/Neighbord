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

-- Índices para consultas frecuentes
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

-- Índice para búsqueda rápida
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
