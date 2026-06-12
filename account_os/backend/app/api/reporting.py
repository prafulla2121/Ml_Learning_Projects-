from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..db.database import get_db_context
from ..api.auth import get_current_user_email
from sqlalchemy import text
from ..agents.reporting import ReportingAgent

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary")
async def get_financial_summary(email: str = Depends(get_current_user_email)):
    """
    Fetches transactions and uses ReportingAgent to generate a summary.
    """
    agent = ReportingAgent()

    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()

        # Fetch synced transactions for reporting
        acc_res = await db.execute(
            text("SELECT amount, gl_code FROM transactions WHERE client_id = :cid AND status = 'synced'"),
            {"cid": client_id}
        )
        transactions = [{"amount": r[0], "gl_code": r[1]} for r in acc_res.fetchall()]

        summary = await agent.generate_summary(transactions)
        cash_flow = await agent.generate_cash_flow(transactions)

        return {
            "p_and_l": summary,
            "cash_flow": cash_flow
        }
