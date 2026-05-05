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