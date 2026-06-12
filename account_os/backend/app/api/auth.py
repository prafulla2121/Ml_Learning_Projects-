from fastapi import Header, HTTPException, APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# Simplified API key validation for the robustness sprint
API_KEYS = {"test-key-123": "test@example.com"}

async def get_current_user_email(x_api_key: str = Header(None), x_user_email: str = Header(...)):
    """
    Identifies the user. Requires an API key for basic security.
    """
    if x_api_key and x_api_key not in API_KEYS:
         raise HTTPException(status_code=403, detail="Invalid API Key")

    if not x_user_email:
        raise HTTPException(status_code=401, detail="X-User-Email header missing")
    return x_user_email

@router.get("/me")
async def get_me(email: str = Header(...)):
    return {"email": email}
