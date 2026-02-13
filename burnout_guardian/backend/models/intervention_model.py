"""
Intervention Model
Stores interventions, actions, and outcomes
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Boolean, Text
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class Intervention(Base):
    """Stores executed interventions"""
    
    __tablename__ = "interventions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Intervention metadata
    intervention_date = Column(DateTime(timezone=True), nullable=False, index=True)
    intervention_type = Column(String, nullable=False)  # buffer, redistribute, alert, manual
    
    # Trigger
    trigger_risk_level = Column(String, nullable=False)  # moderate, high, critical
    trigger_risk_probability = Column(Float, nullable=False)
    trigger_stability_index = Column(Float, nullable=True)
    
    # Action taken
    action_description = Column(Text, nullable=False)
    action_parameters = Column(JSON, default={})
    
    # Calendar buffer specific
    buffer_start_time = Column(DateTime(timezone=True), nullable=True)
    buffer_end_time = Column(DateTime(timezone=True), nullable=True)
    buffer_duration_minutes = Column(Integer, nullable=True)
    calendar_event_id = Column(String, nullable=True)
    
    # Workload redistribution specific
    tasks_redistributed = Column(Integer, default=0)
    workload_reduction_percentage = Column(Float, nullable=True)
    
    # Alert specific
    alert_sent_to = Column(String, nullable=True)  # manager, hr, self
    alert_message = Column(Text, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, executed, failed, cancelled
    execution_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Outcome tracking
    outcome_measured = Column(Boolean, default=False)
    outcome_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Pre-intervention metrics
    pre_stability_index = Column(Float, nullable=True)
    pre_volatility = Column(Float, nullable=True)
    pre_risk_probability = Column(Float, nullable=True)
    
    # Post-intervention metrics (measured after 24-48 hours)
    post_stability_index = Column(Float, nullable=True)
    post_volatility = Column(Float, nullable=True)
    post_risk_probability = Column(Float, nullable=True)
    
    # Effectiveness
    stability_delta = Column(Float, nullable=True)
    volatility_delta = Column(Float, nullable=True)
    risk_delta = Column(Float, nullable=True)
    effectiveness_score = Column(Float, nullable=True)  # 0-1
    
    # User feedback
    user_accepted = Column(Boolean, nullable=True)
    user_feedback = Column(Text, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5
    
    # Metadata
    is_autonomous = Column(Boolean, default=True)
    created_by = Column(String, default="system")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Intervention {self.intervention_type} - {self.user_id} - {self.intervention_date}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "intervention_date": self.intervention_date.isoformat() if self.intervention_date else None,
            "intervention_type": self.intervention_type,
            "trigger_risk_level": self.trigger_risk_level,
            "trigger_risk_probability": self.trigger_risk_probability,
            "action_description": self.action_description,
            "action_parameters": self.action_parameters,
            "status": self.status,
            "execution_timestamp": self.execution_timestamp.isoformat() if self.execution_timestamp else None,
            "outcome_measured": self.outcome_measured,
            "effectiveness_score": self.effectiveness_score,
            "stability_delta": self.stability_delta,
            "user_accepted": self.user_accepted,
            "user_rating": self.user_rating,
            "is_autonomous": self.is_autonomous
        }


class ReinforcementLearning(Base):
    """Stores reinforcement learning state and weights"""
    
    __tablename__ = "reinforcement_learning"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Intervention type
    intervention_type = Column(String, nullable=False)
    
    # Q-values (state-action values)
    q_value = Column(Float, default=0.0)
    
    # Weights for different intervention strategies
    buffer_weight = Column(Float, default=1.0)
    redistribute_weight = Column(Float, default=1.0)
    alert_weight = Column(Float, default=1.0)
    
    # Personalized thresholds
    risk_threshold_buffer = Column(Float, default=0.60)
    risk_threshold_redistribute = Column(Float, default=0.75)
    risk_threshold_alert = Column(Float, default=0.85)
    
    # Learning parameters
    learning_rate = Column(Float, default=0.01)
    discount_factor = Column(Float, default=0.95)
    exploration_rate = Column(Float, default=0.1)
    
    # Performance tracking
    total_interventions = Column(Integer, default=0)
    successful_interventions = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Average effectiveness by type
    avg_effectiveness_buffer = Column(Float, nullable=True)
    avg_effectiveness_redistribute = Column(Float, nullable=True)
    avg_effectiveness_alert = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ReinforcementLearning {self.user_id} - {self.intervention_type}>"


class AuditLog(Base):
    """Audit log for all system actions"""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Actor
    user_id = Column(String, nullable=True, index=True)
    actor_type = Column(String, default="system")  # system, user, admin
    
    # Action
    action_type = Column(String, nullable=False, index=True)
    action_description = Column(Text, nullable=False)
    action_parameters = Column(JSON, default={})
    
    # Target
    target_type = Column(String, nullable=True)  # user, intervention, forecast, etc.
    target_id = Column(String, nullable=True)
    
    # Result
    result = Column(String, default="success")  # success, failure, partial
    error_message = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action_type} - {self.created_at}>"
