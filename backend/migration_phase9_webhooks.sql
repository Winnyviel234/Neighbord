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