"""
Task API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.user_model import User
from backend.models.management_model import Task, TaskLog
from backend.services.auth_service import get_current_user, check_manager_role
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to_id: str
    expected_hours: float
    deadline: datetime
    priority: str = "Medium"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    manager: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Manager only: Assign a task to an employee"""
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        manager_id=manager.id,
        assigned_to_id=task_in.assigned_to_id,
        expected_hours=task_in.expected_hours,
        deadline=task_in.deadline,
        priority=task_in.priority
    )
    db.add(new_task)
    db.commit()
    return {"status": "success", "task_id": new_task.id}

@router.get("/my-assignments")
async def get_my_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to the current user"""
    tasks = db.query(Task).filter(Task.assigned_to_id == user.id).all()
    # Manual serialization since relationships were removed
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "deadline": t.deadline.isoformat(),
            "priority": t.priority
        } for t in tasks
    ]

@router.post("/{task_id}/log-work")
async def log_work(
    task_id: str,
    hours: float,
    notes: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log work hours for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    log = TaskLog(
        task_id=task_id,
        user_id=user.id,
        hours_logged=hours,
        notes=notes
    )
    
    task.actual_hours += hours
    db.add(log)
    db.commit()
    
    # Check for mismatch alert
    if task.actual_hours > task.expected_hours * 1.5:
        return {"status": "warning", "message": "Burnout risk increased due to task mismatch"}
        
    return {"status": "success"}
