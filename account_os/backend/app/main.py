from fastapi import FastAPI

app = FastAPI(title="AccountOS API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Welcome to AccountOS API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
