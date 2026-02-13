from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from loguru import logger
import traceback

from backend.database import get_db
from backend.models.user_model import User
from backend.models.management_model import Task, TaskLog
from backend.services.auth_service import get_current_user, check_manager_role
from backend.services.email_service import send_assignment_email

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    title: str = Form(...),
    description: str = Form(...),
    assigned_to_id: str = Form(...),
    expected_hours: float = Form(...),
    deadline: str = Form(...),
    priority: str = Form("Medium"),
    file: Optional[UploadFile] = File(None),
    manager: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Manager only: Assign a task with optional binary intelligence attachment"""
    try:
        # 1. Verify Asset
        recipient = db.query(User).filter(User.id == assigned_to_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Target asset not found")

        # Parse deadline
        try:
            # Handle ISO format from JavaScript
            # JS toISOString returns YYYY-MM-DDTHH:mm:ss.sssZ
            deadline_clean = deadline.replace('Z', '+00:00')
            deadline_dt = datetime.fromisoformat(deadline_clean)
        except Exception as e:
            logger.warning(f"Deadline parsing fall-back: {e}")
            deadline_dt = datetime.now()

        # 2. Persist Task
        new_task = Task(
            title=title,
            description=description,
            manager_id=manager.id,
            assigned_to_id=assigned_to_id,
            expected_hours=expected_hours,
            deadline=deadline_dt,
            priority=priority
        )
        db.add(new_task)
        db.commit()

        # 3. Execute SMTP Dispatch with Intelligence
        attachment_bytes = None
        attachment_name = None
        if file:
            attachment_bytes = await file.read()
            attachment_name = file.filename

        # Intelligence Check: Is this a dummy domain?
        if recipient.email.endswith("@burnoutguardian.ai"):
            logger.warning(f"⚠️ TARGET ASSET {recipient.full_name} IS USING A DUMMY DOMAIN: {recipient.email}")

        # Execute dispatch (Simulation Mode)
        await send_assignment_email(
            recipient_email=recipient.email,
            recipient_name=recipient.full_name,
            task_title=title,
            task_details=description,
            deadline=deadline_dt.strftime("%Y-%m-%d %H:%M"),
            attachment_data=attachment_bytes,
            attachment_filename=attachment_name
        )

        return {"status": "success", "task_id": new_task.id}
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"❌ TACTICAL DEPLOYMENT FAILURE: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal Intelligence Failure: {str(e)}")

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
