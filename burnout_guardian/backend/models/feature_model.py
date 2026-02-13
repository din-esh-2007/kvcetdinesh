"""
Feature Model
Stores engineered behavioral features
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class BehavioralFeature(Base):
    """Stores daily behavioral features for each user"""
    
    __tablename__ = "behavioral_features"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Date
    feature_date = Column(DateTime(timezone=True), nullable=False, index=True)
    day_index = Column(Integer, nullable=False)
    
    # Workload Signals
    total_work_hours = Column(Float, default=0.0)
    meeting_hours = Column(Float, default=0.0)
    meeting_count = Column(Integer, default=0)
    after_hours_work = Column(Float, default=0.0)
    task_assigned_count = Column(Integer, default=0)
    task_completed_count = Column(Integer, default=0)
    deadline_compression_ratio = Column(Float, default=0.0)
    task_switching_rate = Column(Float, default=0.0)
    email_volume = Column(Integer, default=0)
    slack_message_count = Column(Integer, default=0)
    response_latency_avg = Column(Float, default=0.0)
    
    # Recovery Signals
    longest_focus_block_minutes = Column(Float, default=0.0)
    recovery_gap_minutes = Column(Float, default=0.0)
    weekend_work_ratio = Column(Float, default=0.0)
    sleep_hours = Column(Float, default=7.5)
    sleep_consistency_score = Column(Float, default=0.8)
    hr_variability_index = Column(Float, default=60.0)
    
    # Performance Signals
    error_rate = Column(Float, default=0.0)
    revision_count = Column(Integer, default=0)
    decision_reversal_count = Column(Integer, default=0)
    output_score = Column(Float, default=80.0)
    productivity_volatility_index = Column(Float, default=0.15)
    
    # Derived Signals
    meeting_density_ratio = Column(Float, default=0.0)
    load_accumulation_rate = Column(Float, default=0.0)
    recovery_deficit_score = Column(Float, default=0.0)
    instability_index = Column(Float, default=0.0)
    volatility_acceleration = Column(Float, default=0.0)
    
    # Metadata
    data_source = Column(String, default="calendar")  # calendar, manual, hybrid
    completeness_score = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BehavioralFeature {self.user_id} - {self.feature_date}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feature_date": self.feature_date.isoformat() if self.feature_date else None,
            "workload": {
                "total_work_hours": self.total_work_hours,
                "meeting_hours": self.meeting_hours,
                "meeting_count": self.meeting_count,
                "after_hours_work": self.after_hours_work,
                "task_assigned_count": self.task_assigned_count,
                "task_completed_count": self.task_completed_count,
                "deadline_compression_ratio": self.deadline_compression_ratio,
                "task_switching_rate": self.task_switching_rate
            },
            "recovery": {
                "longest_focus_block_minutes": self.longest_focus_block_minutes,
                "recovery_gap_minutes": self.recovery_gap_minutes,
                "sleep_hours": self.sleep_hours,
                "sleep_consistency_score": self.sleep_consistency_score,
                "hr_variability_index": self.hr_variability_index
            },
            "performance": {
                "error_rate": self.error_rate,
                "output_score": self.output_score,
                "productivity_volatility_index": self.productivity_volatility_index
            },
            "derived": {
                "meeting_density_ratio": self.meeting_density_ratio,
                "load_accumulation_rate": self.load_accumulation_rate,
                "recovery_deficit_score": self.recovery_deficit_score,
                "instability_index": self.instability_index,
                "volatility_acceleration": self.volatility_acceleration
            }
        }


class CalendarEvent(Base):
    """Stores calendar events for analysis"""
    
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Event details
    event_id = Column(String, unique=True, nullable=False)
    summary = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Float, nullable=False)
    
    # Event type
    event_type = Column(String, default="meeting")  # meeting, focus_block, buffer, personal
    is_recurring = Column(Boolean, default=False)
    is_all_day = Column(Boolean, default=False)
    
    # Participants
    attendee_count = Column(Integer, default=1)
    is_organizer = Column(Boolean, default=False)
    
    # Status
    status = Column(String, default="confirmed")  # confirmed, tentative, cancelled
    response_status = Column(String, default="accepted")
    
    # Metadata
    is_system_generated = Column(Boolean, default=False)  # True if inserted by our system
    intervention_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CalendarEvent {self.summary} - {self.start_time}>"
