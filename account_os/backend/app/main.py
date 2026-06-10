from fastapi import FastAPI
from account_os.backend.app.api.auth import router as auth_router

app = FastAPI(title="AccountOS API", version="0.1.0")

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AccountOS API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
