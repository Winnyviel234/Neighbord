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