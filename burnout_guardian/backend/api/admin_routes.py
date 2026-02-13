"""
Admin API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.user_model import User
from backend.models.management_model import Department, Suspension
from backend.services.auth_service import check_admin_role, get_password_hash
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str
    employee_id: str
    role: str # Admin, Manager, Employee
    department_id: Optional[str] = None
    mobile_number: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[datetime] = None
    employment_type: str = "Full-Time"
    emergency_contact: Optional[str] = None
    joining_date: Optional[datetime] = None

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Admin only: Create a new user"""
    # Check if exists
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(User).filter(User.employee_id == user_in.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        username=user_in.username,
        employee_id=user_in.employee_id,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        department_id=user_in.department_id,
        mobile_number=user_in.mobile_number,
        gender=user_in.gender,
        address=user_in.address,
        dob=user_in.dob,
        employment_type=user_in.employment_type,
        emergency_contact=user_in.emergency_contact,
        joining_date=user_in.joining_date or datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id}

@router.get("/users", response_model=List[dict])
async def list_users(
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Admin only: List all users"""
    users = db.query(User).all()
    return [u.to_dict() for u in users]

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    reason: str,
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Admin only: Suspend a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_suspended = True
    
    suspension = Suspension(
        user_id=user_id,
        admin_id=admin.id,
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )
    
    db.add(suspension)
    db.commit()
    return {"status": "success", "message": f"User {user.username} suspended until {end_date}"}

@router.post("/users/{user_id}/fire")
async def fire_user(
    user_id: str,
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Admin only: Permanently disable a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_fired = True
    user.is_active = False
    db.commit()
    return {"status": "success", "message": f"User {user.username} fired"}
