import sys
import os
from datetime import datetime, timedelta
import random

# Removed sys.path modification - run from project root

from backend.database import SessionLocal, init_db
from backend.models.user_model import User, DailyCheckIn
from backend.models.feature_model import BehavioralFeature
from backend.models.stability_model import StabilityAssessment, BaselineMetric
from backend.models.forecast_model import BurnoutForecast
from backend.models.intervention_model import Intervention

def seed():
    print("🌱 Seeding database...")
    init_db()
    
    db = SessionLocal()
    
    # Check if demo user exists
    demo_user = db.query(User).filter(User.employee_id == "EMP0001").first()
    if not demo_user:
        demo_user = User(
            employee_id="EMP0001",
            full_name="John Doe",
            role="Engineer",
            department="Engineering",
            email="john.doe@example.com",
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    
    # Add some historical features
    now = datetime.utcnow()
    for i in range(14):
        date = now - timedelta(days=i)
        
        feature = BehavioralFeature(
            user_id=demo_user.employee_id,
            feature_date=date,
            total_work_hours=8.5 + random.uniform(-1, 2),
            meeting_hours=2.0 + random.uniform(-1, 3),
            meeting_count=random.randint(2, 6),
            task_switching_rate=3.0 + random.uniform(0, 5),
            sleep_hours=7.0 + random.uniform(-2, 1),
            longest_focus_block_minutes=90 + random.uniform(-30, 30),
            error_rate=0.05 + random.uniform(0, 0.1),
            instability_index=0.3 + (i/28),  # Increasing instability
            productivity_volatility_index=0.2 + (i/50)
        )
        db.add(feature)
        
        assessment = StabilityAssessment(
            user_id=demo_user.employee_id,
            assessment_date=date,
            stability_index=1.0 - feature.instability_index,
            volatility=feature.productivity_volatility_index,
            risk_probability=0.2 + (i/20),
            risk_level="low" if i < 7 else "moderate"
        )
        db.add(assessment)
    
    # Add a forecast
    forecast = BurnoutForecast(
        user_id=demo_user.employee_id,
        forecast_date=now,
        horizon_days=7,
        forecast_values=[0.4, 0.45, 0.52, 0.61, 0.72, 0.81, 0.88],
        forecast_dates=[(now + timedelta(days=i)).isoformat() for i in range(1, 8)],
        peak_risk_probability=0.88,
        tipping_point_detected=1,
        model_type="ensemble"
    )
    db.add(forecast)
    
    db.commit()
    db.close()
    print("✅ Seeding complete!")

if __name__ == "__main__":
    seed()
