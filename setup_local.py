import sqlite3
import os
import uuid
from datetime import date, timedelta

def setup():
    db_path = "account_os.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Try to find schema.sql
    schema_path = "account_os/backend/app/db/schema.sql"
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found.")
        return

    with open(schema_path, "r") as f:
        schema = f.read()

    # SQLite Adaptations
    schema = schema.replace("gen_random_uuid()", "'UUID-' || hex(randomblob(4))")
    schema = schema.replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
    schema = schema.replace("JSONB", "TEXT")
    schema = schema.replace("UUID", "TEXT")

    lines = schema.splitlines()
    filtered_lines = [l for l in lines if "ROW LEVEL SECURITY" not in l and "CREATE POLICY" not in l and "USING" not in l]
    schema = "\n".join(filtered_lines)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.executescript(schema)
    except Exception as e:
        print(f"Schema script error: {e}. Falling back to manual minimal schema...")
        cursor.execute("CREATE TABLE clients (id TEXT PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE users (id TEXT PRIMARY KEY, client_id TEXT, email TEXT UNIQUE, full_name TEXT)")
        cursor.execute("CREATE TABLE transactions (id TEXT PRIMARY KEY, client_id TEXT, entity_id TEXT, vendor_name TEXT, amount REAL, status TEXT, gl_code TEXT, transaction_date TEXT, currency TEXT)")
        cursor.execute("CREATE TABLE rules (id TEXT PRIMARY KEY, client_id TEXT, configuration TEXT)")
        cursor.execute("CREATE TABLE credentials (id TEXT PRIMARY KEY, client_id TEXT, platform TEXT, encrypted_data TEXT)")

    # Seed Demo Data
    client_id = "client-demo-id"
    cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (client_id, "Satva Solutions Demo"))
    cursor.execute("INSERT INTO users (id, client_id, email, full_name) VALUES (?, ?, ?, ?)",
                   (str(uuid.uuid4()), client_id, "test@example.com", "Chartered Accountant"))

    # Seed Rules
    cursor.execute("INSERT INTO rules (id, client_id, configuration) VALUES (?, ?, ?)",
                   (str(uuid.uuid4()), client_id, '{"field": "vendor_name", "operator": "contains", "value": "Amazon", "target_gl": "6200"}'))

    conn.commit()
    conn.close()
    print("✅ Local environment initialized with real business context.")

if __name__ == "__main__":
    setup()
