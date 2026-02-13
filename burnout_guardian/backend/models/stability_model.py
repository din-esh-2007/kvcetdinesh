"""
Stability Model
Stores stability assessments and risk scores
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class StabilityAssessment(Base):
    """Stores daily stability assessments"""
    
    __tablename__ = "stability_assessments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Date
    assessment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Core Stability Metrics
    stability_index = Column(Float, nullable=False)  # 0-1, higher is better
    volatility = Column(Float, nullable=False)  # 0-1, lower is better
    acceleration = Column(Float, nullable=False)  # Rate of change
    
    # Risk Assessment
    risk_probability = Column(Float, nullable=False)  # 0-1, collapse probability
    risk_level = Column(String, nullable=False)  # low, moderate, high, critical
    
    # Contributing Factors (JSON array of top contributors)
    top_contributors = Column(JSON, default=[])
    
    # Anomaly Detection
    is_anomaly = Column(Integer, default=0)  # 1 if anomaly detected, -1 if normal
    anomaly_score = Column(Float, default=0.0)
    
    # Change Point Detection
    is_change_point = Column(Integer, default=0)  # 1 if change point detected
    change_point_probability = Column(Float, default=0.0)
    
    # Baseline Comparison
    baseline_deviation = Column(Float, default=0.0)
    baseline_window_start = Column(DateTime(timezone=True), nullable=True)
    baseline_window_end = Column(DateTime(timezone=True), nullable=True)
    
    # Hybrid Score (behavioral + emotional + self-report)
    behavioral_score = Column(Float, default=0.0)
    emotional_score = Column(Float, nullable=True)
    selfreport_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    
    # Metadata
    model_version = Column(String, default="1.0")
    confidence_score = Column(Float, default=0.8)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<StabilityAssessment {self.user_id} - {self.assessment_date} - Risk: {self.risk_level}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_date": self.assessment_date.isoformat() if self.assessment_date else None,
            "stability_index": self.stability_index,
            "volatility": self.volatility,
            "acceleration": self.acceleration,
            "risk_probability": self.risk_probability,
            "risk_level": self.risk_level,
            "top_contributors": self.top_contributors,
            "is_anomaly": bool(self.is_anomaly == 1),
            "anomaly_score": self.anomaly_score,
            "is_change_point": bool(self.is_change_point == 1),
            "change_point_probability": self.change_point_probability,
            "baseline_deviation": self.baseline_deviation,
            "hybrid_score": self.hybrid_score,
            "confidence_score": self.confidence_score
        }


class BaselineMetric(Base):
    """Stores rolling baseline metrics for comparison"""
    
    __tablename__ = "baseline_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Window
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    window_days = Column(Integer, default=7)
    
    # Baseline Statistics
    mean_stability = Column(Float, default=0.0)
    std_stability = Column(Float, default=0.0)
    mean_volatility = Column(Float, default=0.0)
    std_volatility = Column(Float, default=0.0)
    
    # Workload Baselines
    mean_work_hours = Column(Float, default=0.0)
    mean_meeting_hours = Column(Float, default=0.0)
    mean_task_switching = Column(Float, default=0.0)
    
    # Recovery Baselines
    mean_sleep_hours = Column(Float, default=0.0)
    mean_focus_block = Column(Float, default=0.0)
    mean_recovery_gap = Column(Float, default=0.0)
    
    # Performance Baselines
    mean_error_rate = Column(Float, default=0.0)
    mean_output_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BaselineMetric {self.user_id} - {self.window_start} to {self.window_end}>"
