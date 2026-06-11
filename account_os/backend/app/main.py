from fastapi import FastAPI
from account_os.backend.app.api.auth import router as auth_router
from account_os.backend.app.api.documents import router as doc_router
from account_os.backend.app.api.sync import router as sync_router
from account_os.backend.app.api.payments import router as payment_router

app = FastAPI(title="AccountOS API", version="0.1.0")

app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(sync_router)
app.include_router(payment_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AccountOS API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
