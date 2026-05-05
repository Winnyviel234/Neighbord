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