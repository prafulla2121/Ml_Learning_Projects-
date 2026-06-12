from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..engine.billing import BillingService
from ..api.auth import get_current_user_email
from ..db.database import get_db_context
from sqlalchemy import text

router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/status")
async def get_status(email: str = Depends(get_current_user_email)):
    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()
        return await BillingService.get_billing_status(str(client_id))

@router.post("/subscribe")
async def subscribe(plan: str, email: str = Depends(get_current_user_email)):
    async with get_db_context() as db:
        res = await db.execute(text("SELECT client_id FROM users WHERE email = :email"), {"email": email})
        client_id = res.scalar_one()
        return await BillingService.create_subscription(str(client_id), plan)
