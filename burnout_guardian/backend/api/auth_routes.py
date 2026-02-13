"""
Auth API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.database import get_db
from backend.models.user_model import User
from backend.services.auth_service import verify_password, create_access_token, get_password_hash, get_current_user
from backend.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate a user and return a JWT"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        # Fallback to employee_id
        user = db.query(User).filter(User.employee_id == form_data.username).first()
        
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")
        
    if user.is_fired:
        raise HTTPException(status_code=403, detail="Account is permanently disabled")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username or user.employee_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username or user.employee_id
    }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get profile of current authenticated user"""
    return current_user.to_dict()
