from fastapi import FastAPI
from account_os.backend.app.api.auth import router as auth_router
from account_os.backend.app.api.documents import router as doc_router
from account_os.backend.app.api.sync import router as sync_router
from account_os.backend.app.api.payments import router as payment_router
from account_os.backend.app.api.reconciliation import router as reconciliation_router
from account_os.backend.app.api.reporting import router as reporting_router
from account_os.backend.app.api.billing import router as billing_router
from account_os.backend.app.api.payroll import router as payroll_router
from account_os.backend.app.db.database import get_db_context
from sqlalchemy import text

app = FastAPI(title="AccountOS API", version="0.1.0")

app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(sync_router)
app.include_router(payment_router)
app.include_router(reconciliation_router)
app.include_router(reporting_router)
app.include_router(billing_router)
app.include_router(payroll_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AccountOS API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

from fastapi import Header
@app.get("/transactions")
async def list_transactions(x_user_email: str = Header(...)):
    async with get_db_context(user_email=x_user_email) as db:
        res = await db.execute(text("SELECT id, vendor_name, amount, status, gl_code, transaction_date FROM transactions"))
        rows = res.fetchall()
        return [
            {"id": r[0], "vendor_name": r[1], "amount": r[2], "status": r[3], "gl_code": r[4], "transaction_date": r[5]}
            for r in rows
        ]
