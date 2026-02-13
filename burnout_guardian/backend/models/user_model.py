"""
User Model
Stores user profiles, authentication, and preferences
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identity & Auth
    username = Column(String, unique=True, nullable=True, index=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile Details (New Requirements)
    mobile_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    dob = Column(DateTime, nullable=True)
    employment_type = Column(String, default="Full-Time") # Full-time, Contract, Part-time
    emergency_contact = Column(String, nullable=True)
    joining_date = Column(DateTime, nullable=True)
    
    # Status & Security
    is_active = Column(Boolean, default=True)
    is_fired = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Role & Org
    role = Column(String, default="Employee")  # Admin, Manager, Employee
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(String, nullable=True)
    
    # Preferences (New Requirements)
    language = Column(String, default="English") # English, Tamil
    theme = Column(String, default="Premium") # White, Black, Premium
    cv_opt_in = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)
    
    # Baseline Metrics
    baseline_resilience = Column(Float, default=0.7)
    resilience_threshold = Column(Float, default=0.6)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User {self.username or self.employee_id} - {self.role}>"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "employee_id": self.employee_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "department_id": self.department_id,
            "mobile_number": self.mobile_number,
            "gender": self.gender,
            "address": self.address,
            "dob": self.dob.isoformat() if self.dob else None,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "employment_type": self.employment_type,
            "emergency_contact": self.emergency_contact,
            "is_active": self.is_active,
            "is_suspended": self.is_suspended,
            "cv_opt_in": self.cv_opt_in,
            "notification_enabled": self.notification_enabled,
            "baseline_resilience": self.baseline_resilience,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class DailyCheckIn(Base):
    """Daily self-reported check-in data"""
    
    __tablename__ = "daily_checkins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Date
    checkin_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Self-reported metrics
    sleep_hours = Column(Float, nullable=False)
    work_hours_planned = Column(Float, nullable=True)
    mood_rating = Column(Integer, nullable=False)  # 1-10
    stress_level = Column(Integer, nullable=False)  # 1-10
    energy_level = Column(Integer, nullable=False)  # 1-10
    
    # Additional context
    meeting_count_expected = Column(Integer, default=0)
    caffeine_intake = Column(Integer, default=0)  # cups
    exercise_minutes = Column(Integer, default=0)
    
    # Notes
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DailyCheckIn {self.user_id} - {self.checkin_date}>"


class EmotionCapture(Base):
    """Computer vision emotion detection captures"""
    
    __tablename__ = "emotion_captures"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Timestamp
    captured_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Emotion probabilities (from DeepFace)
    happy = Column(Float, default=0.0)
    sad = Column(Float, default=0.0)
    angry = Column(Float, default=0.0)
    neutral = Column(Float, default=0.0)
    fear = Column(Float, default=0.0)
    surprise = Column(Float, default=0.0)
    disgust = Column(Float, default=0.0)
    
    # Derived metrics
    stress_proxy = Column(Float, default=0.0)  # angry + fear + sad
    emotional_stability_index = Column(Float, default=0.0)
    
    # Metadata
    confidence_score = Column(Float, default=0.0)
    face_detected = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<EmotionCapture {self.user_id} - {self.captured_at}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "emotions": {
                "happy": self.happy,
                "sad": self.sad,
                "angry": self.angry,
                "neutral": self.neutral,
                "fear": self.fear,
                "surprise": self.surprise,
                "disgust": self.disgust
            },
            "stress_proxy": self.stress_proxy,
            "emotional_stability_index": self.emotional_stability_index,
            "confidence_score": self.confidence_score
        }
