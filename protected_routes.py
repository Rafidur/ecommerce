# app/routers/protected_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from auth.jwt import oauth2_scheme, verify_token

router = APIRouter()

# Dependency to extract and validate the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

# Example of a protected route
@router.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
