from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from ..db.database import get_db_context
from sqlalchemy import text
import uuid

router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentSchedule(BaseModel):
    transaction_id: str
    amount: float
    scheduled_date: date
    payment_method: str = "ACH"

from .auth import get_current_user_email

@router.post("/schedule")
async def schedule_payment(payment: PaymentSchedule, email: str = Depends(get_current_user_email)):
    """
    Schedules a payment for a specific bill/transaction.
    """
    async with get_db_context(user_email=email) as db:
        # Get client_id from email
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()

        payment_id = str(uuid.uuid4())
        await db.execute(
            text("INSERT INTO payments (id, client_id, transaction_id, amount, scheduled_date, status, payment_method) VALUES (:id, :client_id, :tx_id, :amount, :date, 'scheduled', :method)"),
            {
                "id": payment_id,
                "client_id": client_id,
                "tx_id": payment.transaction_id,
                "amount": payment.amount,
                "date": payment.scheduled_date,
                "method": payment.payment_method
            }
        )
        await db.commit()
        return {"payment_id": payment_id, "status": "scheduled"}

@router.get("/")
async def list_payments(email: str = Depends(get_current_user_email)):
    """
    Lists all scheduled payments.
    """
    async with get_db_context(user_email=email) as db:
        result = await db.execute(text("SELECT id, transaction_id, amount, scheduled_date, status FROM payments"))
        payments = result.fetchall()
        return [
            {"id": p[0], "transaction_id": p[1], "amount": p[2], "scheduled_date": p[3], "status": p[4]}
            for p in payments
        ]

@router.post("/{payment_id}/cancel")
async def cancel_payment(payment_id: str, email: str = Depends(get_current_user_email)):
    """
    Cancels a scheduled payment.
    """
    async with get_db_context(user_email=email) as db:
        await db.execute(
            text("UPDATE payments SET status = 'cancelled' WHERE id = :id"),
            {"id": payment_id}
        )
        await db.commit()
        return {"status": "cancelled"}
