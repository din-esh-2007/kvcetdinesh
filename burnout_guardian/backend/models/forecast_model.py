"""
Forecast Model
Stores burnout forecasts and predictions
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class BurnoutForecast(Base):
    """Stores burnout probability forecasts"""
    
    __tablename__ = "burnout_forecasts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Forecast metadata
    forecast_date = Column(DateTime(timezone=True), nullable=False, index=True)
    horizon_days = Column(Integer, default=7)
    
    # Forecast values (JSON array of daily probabilities)
    forecast_values = Column(JSON, nullable=False)  # [day1, day2, ..., day7]
    forecast_dates = Column(JSON, nullable=False)  # [date1, date2, ..., date7]
    
    # Confidence intervals
    lower_bound = Column(JSON, nullable=True)
    upper_bound = Column(JSON, nullable=True)
    
    # Peak risk
    peak_risk_date = Column(DateTime(timezone=True), nullable=True)
    peak_risk_probability = Column(Float, nullable=True)
    
    # Tipping point detection
    tipping_point_detected = Column(Integer, default=0)
    tipping_point_date = Column(DateTime(timezone=True), nullable=True)
    tipping_point_probability = Column(Float, nullable=True)
    
    # Model used
    model_type = Column(String, default="prophet")  # prophet, lstm, ensemble
    model_version = Column(String, default="1.0")
    
    # Performance metrics
    mae = Column(Float, nullable=True)  # Mean Absolute Error
    rmse = Column(Float, nullable=True)  # Root Mean Squared Error
    confidence_score = Column(Float, default=0.8)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BurnoutForecast {self.user_id} - {self.forecast_date} - {self.horizon_days}d>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None,
            "horizon_days": self.horizon_days,
            "forecast_values": self.forecast_values,
            "forecast_dates": self.forecast_dates,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "peak_risk_date": self.peak_risk_date.isoformat() if self.peak_risk_date else None,
            "peak_risk_probability": self.peak_risk_probability,
            "tipping_point_detected": bool(self.tipping_point_detected == 1),
            "tipping_point_date": self.tipping_point_date.isoformat() if self.tipping_point_date else None,
            "tipping_point_probability": self.tipping_point_probability,
            "model_type": self.model_type,
            "confidence_score": self.confidence_score
        }


class LSTMPrediction(Base):
    """Stores LSTM model predictions"""
    
    __tablename__ = "lstm_predictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Prediction metadata
    prediction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    sequence_length = Column(Integer, default=14)
    
    # Predictions
    predicted_values = Column(JSON, nullable=False)
    predicted_dates = Column(JSON, nullable=False)
    
    # Model state
    hidden_state = Column(JSON, nullable=True)
    cell_state = Column(JSON, nullable=True)
    
    # Performance
    loss = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<LSTMPrediction {self.user_id} - {self.prediction_date}>"
