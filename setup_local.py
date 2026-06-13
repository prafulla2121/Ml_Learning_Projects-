import sqlite3
import os
import uuid
from datetime import date, timedelta

def setup():
    db_path = "account_os.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    with open("account_os/backend/app/db/schema.sql", "r") as f:
        schema = f.read()

    # SQLite Adaptations
    schema = schema.replace("gen_random_uuid()", "'MOCK-UUID'")
    schema = schema.replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
    schema = schema.replace("JSONB", "TEXT")
    schema = schema.replace("UUID", "TEXT")

    lines = schema.splitlines()
    filtered_lines = [l for l in lines if "ROW LEVEL SECURITY" not in l and "CREATE POLICY" not in l and "USING" not in l]
    schema = "\n".join(filtered_lines)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)

    # Seed Demo Data
    client_id = "client-demo-id"
    cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (client_id, "Satva Demo Client"))
    cursor.execute("INSERT INTO users (client_id, email, full_name) VALUES (?, ?, ?)", (client_id, "test@example.com", "Demo User"))

    # Seed some transactions
    today = date.today()
    txs = [
        (str(uuid.uuid4()), client_id, "Amazon", 249.99, "USD", today - timedelta(days=1), "synced", "6200"),
        (str(uuid.uuid4()), client_id, "Starbucks", 15.40, "USD", today, "synced", "6300"),
        (str(uuid.uuid4()), client_id, "Uber", 42.10, "USD", today - timedelta(days=2), "synced", "6400"),
    ]
    for tx in txs:
        # Note: SQLite doesn't natively handle 'date' objects well in executescript/execute without custom adapters,
        # so we convert to string
        cursor.execute("INSERT INTO transactions (id, client_id, vendor_name, amount, currency, transaction_date, status, gl_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (tx[0], tx[1], tx[2], tx[3], tx[4], str(tx[5]), tx[6], tx[7]))

    conn.commit()
    conn.close()
    print("✅ Environment setup complete. Run 'cd account_os/backend && uvicorn app.main:app' to start.")

if __name__ == "__main__":
    setup()
