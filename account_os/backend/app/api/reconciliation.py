from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
from ..db.database import get_db_context
from ..api.auth import get_current_user_email
from sqlalchemy import text
from ..agents.reconciliation import ReconciliationAgent
import csv
import io
import uuid
from datetime import datetime

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])

@router.post("/upload")
async def upload_bank_statement(
    file: UploadFile = File(...),
    email: str = Depends(get_current_user_email)
):
    """
    Ingests a bank statement CSV and stores transactions.
    """
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()

        transactions_count = 0
        for row in reader:
            await db.execute(
                text("INSERT INTO bank_transactions (id, client_id, description, amount, transaction_date) VALUES (:id, :client_id, :desc, :amount, :date)"),
                {
                    "id": str(uuid.uuid4()),
                    "client_id": client_id,
                    "desc": row.get("Description", row.get("description")),
                    "amount": float(row.get("Amount", row.get("amount", 0))),
                    "date": row.get("Date", row.get("date"))
                }
            )
            transactions_count += 1

        await db.commit()

    return {"status": "success", "transactions_imported": transactions_count}

@router.post("/run")
async def run_reconciliation(email: str = Depends(get_current_user_email)):
    """
    Runs the ReconciliationAgent to match bank transactions to accounting entries.
    """
    agent = ReconciliationAgent()

    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()

        # Fetch unreconciled bank transactions
        bank_res = await db.execute(
            text("SELECT id, description, amount, transaction_date FROM bank_transactions WHERE client_id = :cid AND status = 'unreconciled'"),
            {"cid": client_id}
        )
        bank_txs = [{"id": r[0], "description": r[1], "amount": r[2], "transaction_date": r[3]} for r in bank_res.fetchall()]

        # Fetch synced accounting transactions
        acc_res = await db.execute(
            text("SELECT id, vendor_name, amount, transaction_date FROM transactions WHERE client_id = :cid AND status = 'synced'"),
            {"cid": client_id}
        )
        acc_txs = [{"id": r[0], "vendor_name": r[1], "amount": r[2], "transaction_date": r[3]} for r in acc_res.fetchall()]

        results = await agent.match_transactions(bank_txs, acc_txs)

        # Save matches
        for match in results["matches"]:
            await db.execute(
                text("INSERT INTO reconciliation_matches (bank_transaction_id, accounting_transaction_id, confidence) VALUES (:bid, :aid, :conf)"),
                {
                    "bid": match["bank_transaction"]["id"],
                    "aid": match["accounting_entry"]["id"],
                    "conf": match["confidence"]
                }
            )
            # Update status
            await db.execute(
                text("UPDATE bank_transactions SET status = 'reconciled' WHERE id = :bid"),
                {"bid": match["bank_transaction"]["id"]}
            )

        await db.commit()

    return {"matches_found": len(results["matches"])}
