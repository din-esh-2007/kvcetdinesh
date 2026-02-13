"""
Management Models
Stores departments, tasks, and suspensions
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class Department(Base):
    """Organizational departments"""
    __tablename__ = "departments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    """Task assignments and tracking"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Assignment
    manager_id = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timing
    expected_hours = Column(Float, nullable=False)
    actual_hours = Column(Float, default=0.0)
    deadline = Column(DateTime(timezone=True), nullable=False)
    priority = Column(String, default="Medium")  # Low, Medium, High, Critical
    
    # Status
    status = Column(String, default="Pending")  # Pending, In Progress, Completed, Delayed
    revision_count = Column(Integer, default=0)
    is_split = Column(Boolean, default=False)
    
    # Metadata
    task_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class TaskLog(Base):
    """Daily logs for tasks"""
    __tablename__ = "task_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    hours_logged = Column(Float, nullable=False)
    log_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)


class Suspension(Base):
    """User suspension records"""
    __tablename__ = "suspensions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
