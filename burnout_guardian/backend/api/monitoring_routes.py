from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.user_model import User, DailyCheckIn
from backend.models.stability_model import StabilityAssessment
from backend.models.intervention_model import Intervention
from backend.services.auth_service import check_admin_role

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

@router.get("/aggregate-stats")
async def get_aggregate_stats(
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Get high-level stats for the admin dashboard"""
    # 1. Total Employees
    total_users = db.query(User).filter(User.role == "Employee").count()
    
    # 2. High Risk Count (last 24 hours)
    last_24h = datetime.now() - timedelta(hours=24)
    high_risk = db.query(StabilityAssessment).filter(
        StabilityAssessment.assessment_date >= last_24h,
        StabilityAssessment.risk_level.in_(["high", "critical"])
    ).distinct(StabilityAssessment.user_id).count()
    
    # 3. Active Interventions (last 24 hours)
    active_interventions = db.query(Intervention).filter(
        Intervention.intervention_date >= last_24h
    ).count()
    
    # 4. Avg stability (last 7 days)
    last_7d = datetime.now() - timedelta(days=7)
    avg_stability = db.query(func.avg(StabilityAssessment.stability_index)).filter(
        StabilityAssessment.assessment_date >= last_7d
    ).scalar() or 0.85

    return {
        "total_assets": total_users,
        "high_risk_assets": high_risk,
        "autonomous_interventions": active_interventions,
        "org_stability_index": round(float(avg_stability), 2)
    }

@router.get("/chart-data")
async def get_chart_data(
    admin: User = Depends(check_admin_role),
    db: Session = Depends(get_db)
):
    """Get data for admin dashboard charts"""
    last_7d = datetime.now() - timedelta(days=7)
    
    # 1. Stability Trend (Avg index per day)
    stability_trend = db.query(
        func.cast(StabilityAssessment.assessment_date, func.Date).label('date'),
        func.avg(StabilityAssessment.stability_index).label('avg_idx')
    ).filter(StabilityAssessment.assessment_date >= last_7d).group_by('date').order_by('date').all()

    # 2. Risk Distribution (Count per risk level)
    risk_dist = db.query(
        StabilityAssessment.risk_level,
        func.count(StabilityAssessment.id)
    ).filter(StabilityAssessment.assessment_date >= datetime.now() - timedelta(hours=24)).group_by(StabilityAssessment.risk_level).all()

    # 3. Intervention Effectiveness (Comparison)
    interventions = db.query(
        Intervention.intervention_type,
        func.avg(Intervention.effectiveness_score)
    ).group_by(Intervention.intervention_type).all()

    return {
        "stability": [{"date": str(r.date), "value": float(r.avg_idx)} for r in stability_trend],
        "risk": {r[0]: r[1] for r in risk_dist},
        "interventions": {r[0]: float(r[1]) for r in interventions}
    }
