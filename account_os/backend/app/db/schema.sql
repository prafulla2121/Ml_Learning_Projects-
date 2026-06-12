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

-- NOTE: For SQLite compatibility in local development:
-- JSONB -> TEXT
-- UUID -> TEXT
-- gen_random_uuid() -> random hex string
-- TIMESTAMP WITH TIME ZONE -> TIMESTAMP

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Entities table (Sub-tenants/Branches/Subsidiaries)
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    name TEXT NOT NULL,
    country TEXT,
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE entities ENABLE ROW LEVEL SECURITY;

-- Learning Loop Table (Corrections)
CREATE TABLE corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    vendor_name TEXT NOT NULL,
    original_gl_code TEXT,
    corrected_gl_code TEXT NOT NULL,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;

-- Invoices Table (AR)
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    entity_id UUID REFERENCES entities(id),
    customer_name TEXT NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    due_date DATE,
    status TEXT DEFAULT 'draft', -- draft, sent, paid, overdue
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Reminders Table
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id),
    reminder_type TEXT, -- email, whatsapp
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT
);

ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;

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
    entity_id UUID REFERENCES entities(id),
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
    entity_id UUID REFERENCES entities(id),
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
    entity_id UUID REFERENCES entities(id),
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

-- For Entities
CREATE POLICY client_entities_isolation_policy ON entities
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- For Corrections
CREATE POLICY client_corrections_isolation_policy ON corrections
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- For Invoices
CREATE POLICY client_invoices_isolation_policy ON invoices
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- Audit Logs Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    entity_id UUID REFERENCES entities(id),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY client_audit_isolation_policy ON audit_logs
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- Payments table (AP)
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    transaction_id UUID REFERENCES transactions(id),
    amount NUMERIC(15, 2) NOT NULL,
    scheduled_date DATE,
    status TEXT DEFAULT 'scheduled', -- scheduled, processing, paid, failed, cancelled
    payment_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY client_payments_isolation_policy ON payments
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- Bank Transactions table
CREATE TABLE bank_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    entity_id UUID REFERENCES entities(id),
    bank_account_id TEXT,
    transaction_date DATE,
    description TEXT,
    amount NUMERIC(15, 2),
    currency TEXT DEFAULT 'USD',
    external_id TEXT, -- platform specific bank transaction id
    status TEXT DEFAULT 'unreconciled', -- unreconciled, reconciled, ignored
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY client_bank_tx_isolation_policy ON bank_transactions
    USING (client_id = (SELECT client_id FROM users WHERE email = current_setting('app.current_user_email')));

-- Reconciliation Matches table
CREATE TABLE reconciliation_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_transaction_id UUID REFERENCES bank_transactions(id),
    accounting_transaction_id UUID REFERENCES transactions(id),
    confidence NUMERIC(3, 2),
    matched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
