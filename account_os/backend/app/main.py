from fastapi import FastAPI
from account_os.backend.app.api.auth import router as auth_router
from account_os.backend.app.api.documents import router as doc_router
from account_os.backend.app.api.sync import router as sync_router
from account_os.backend.app.api.payments import router as payment_router
from account_os.backend.app.api.reconciliation import router as reconciliation_router
from account_os.backend.app.api.reporting import router as reporting_router
from account_os.backend.app.api.billing import router as billing_router
from account_os.backend.app.api.payroll import router as payroll_router

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
