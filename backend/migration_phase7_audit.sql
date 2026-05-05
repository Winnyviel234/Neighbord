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