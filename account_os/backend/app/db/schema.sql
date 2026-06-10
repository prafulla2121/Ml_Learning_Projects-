-- Initial Database Schema for AccountOS

-- Enable Row-Level Security
-- (Note: In a real production environment, we'd use migrations like Alembic)

-- Clients table (Tenants)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    vendor_name TEXT,
    amount NUMERIC(15, 2),
    currency TEXT DEFAULT 'USD',
    transaction_date DATE,
    status TEXT DEFAULT 'pending', -- pending, approved, synced, rejected
    raw_data JSONB,
    gl_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Rules table
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    rule_type TEXT NOT NULL, -- mapping, approval, tax
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE rules ENABLE ROW LEVEL SECURITY;

-- Credentials table for OAuth tokens and API keys
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    platform TEXT NOT NULL, -- qbo, xero, sage, etc.
    encrypted_data JSONB NOT NULL, -- stores access_token, refresh_token, realm_id, etc.
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- For Transactions
CREATE POLICY client_isolation_policy ON transactions
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- For Rules
CREATE POLICY client_rules_isolation_policy ON rules
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- For Clients (Clients can only see their own record)
CREATE POLICY client_self_isolation_policy ON clients
    USING (id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- For Credentials
CREATE POLICY client_credentials_isolation_policy ON credentials
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));
