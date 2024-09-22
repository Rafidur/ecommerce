# app/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from auth.jwt import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.jwt import get_password_hash
from database import get_db
from models import Customer
from schemas import Token

router = APIRouter()

# Route to get access token
@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Route for registering new users
@router.post("/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    new_user = Customer(email=email, password=hashed_password, name="Your Name")
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}
