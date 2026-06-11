from fastapi import Header, HTTPException, APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user_email(x_user_email: str = Header(...)):
    """
    Extracts user email from X-User-Email header.
    In a real app, this would validate a JWT/OAuth token.
    """
    if not x_user_email:
        raise HTTPException(status_code=401, detail="X-User-Email header missing")
    return x_user_email

@router.get("/me")
async def get_me(email: str = Header(...)):
    return {"email": email}
