# app/routers/protected_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.jwt import oauth2_scheme, verify_token
from database import get_db
from models import Customer

router = APIRouter()

# Dependency to extract and validate the current user
def get_current_customer(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token, credentials_exception)
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        raise credentials_exception
    return customer

@router.get("/customers/me")
async def read_customers_me(current_customer: Customer = Depends(get_current_customer)):
    return {"email": current_customer.email, "is_active": current_customer.is_active}