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