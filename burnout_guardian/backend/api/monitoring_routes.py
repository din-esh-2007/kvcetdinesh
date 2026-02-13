from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta
import random
from backend.database import get_db
from backend.models.user_model import User, DailyCheckIn, EmotionCapture
from backend.models.stability_model import StabilityAssessment
from backend.models.forecast_model import BurnoutForecast
from backend.models.intervention_model import Intervention
from backend.services.auth_service import check_admin_role, get_current_user, check_manager_role

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

@router.get("/aggregate-stats")
async def get_aggregate_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get high-level stats for the dashboard"""
    if user.role not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data for dashboard charts"""
    if user.role not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
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

@router.get("/forecast-data")
async def get_forecast_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get forecast data for the 7-day predictive flux graph"""
    # If admin/manager, we could potentially get aggregate or specific. 
    # For now, if no user_id param, return current user's
    target_id = user.id
    
    forecast = db.query(BurnoutForecast).filter(
        BurnoutForecast.user_id == target_id
    ).order_by(BurnoutForecast.forecast_date.desc()).first()
    
    if not forecast:
        # Generate some synthetic forecast if none exists
        now = datetime.now()
        dates = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
        values = [round(random.uniform(0.1, 0.4), 2) for _ in range(7)]
        return {"dates": dates, "values": values}
        
    return {
        "dates": forecast.forecast_dates,
        "values": forecast.forecast_values
    }

@router.get("/emotion-data")
async def get_emotion_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get emotion trend data for the sentiment stream graph"""
    last_24h = datetime.now() - timedelta(hours=24)
    captures = db.query(EmotionCapture).filter(
        EmotionCapture.user_id == user.id,
        EmotionCapture.captured_at >= last_24h
    ).order_by(EmotionCapture.captured_at.asc()).all()
    
    if not captures:
        # Synthetic stream
        now = datetime.now()
        data = []
        for i in range(10):
            t = now - timedelta(minutes=i*30)
            data.append({
                "time": t.strftime("%H:%M"),
                "happy": round(random.uniform(0.4, 0.8), 2),
                "neutral": round(random.uniform(0.1, 0.3), 2),
                "stress": round(random.uniform(0.0, 0.2), 2)
            })
        return data[::-1]
        
    return [
        {
            "time": c.captured_at.strftime("%H:%M"),
            "happy": c.happy,
            "neutral": c.neutral,
            "stress": c.stress_proxy
        } for c in captures
    ]

@router.get("/manager-stats")
async def get_manager_stats(
    manager: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Specific stats for a manager's direct reports"""
    # 1. Get Team IDs
    team_members = db.query(User).filter(User.manager_id == manager.id).all()
    team_ids = [u.id for u in team_members]
    
    if not team_ids:
        return {
            "team_count": 0,
            "avg_stability": 1.0,
            "at_risk_count": 0,
            "recent_checkins": []
        }

    # 2. Avg Team Stability
    avg_stability = db.query(func.avg(StabilityAssessment.stability_index)).filter(
        StabilityAssessment.user_id.in_(team_ids)
    ).scalar() or 0.85

    # 3. At Risk Members (High/Critical)
    at_risk_count = db.query(StabilityAssessment).filter(
        StabilityAssessment.user_id.in_(team_ids),
        StabilityAssessment.risk_level.in_(["high", "critical"])
    ).distinct(StabilityAssessment.user_id).count()

    # 4. Predicted Risk (Avg for team in next 7 days)
    avg_pred_risk = db.query(func.avg(BurnoutForecast.peak_risk_probability)).filter(
        BurnoutForecast.user_id.in_(team_ids)
    ).scalar() or 0.15

    # 5. Recent Check-ins
    recent_checkins = db.query(DailyCheckIn).filter(
        DailyCheckIn.user_id.in_(team_ids)
    ).order_by(DailyCheckIn.checkin_date.desc()).limit(10).all()

    # 6. Detailed Team Stability (for Heatmap)
    # Get last assessment for each team member
    team_analytics = []
    for member in team_members:
        latest = db.query(StabilityAssessment).filter(
            StabilityAssessment.user_id == member.id
        ).order_by(StabilityAssessment.assessment_date.desc()).first()
        if latest:
            team_analytics.append({
                "label": member.full_name,
                "value": latest.stability_index
            })

    return {
        "team_count": len(team_ids),
        "avg_stability": round(float(avg_stability), 2),
        "at_risk_count": at_risk_count,
        "predicted_risk": round(float(avg_pred_risk) * 100, 1),
        "recent_checkins": [
            {
                "user": next((u.full_name for u in team_members if u.id == c.user_id), "Unknown"),
                "mood": c.mood_rating,
                "workload": c.stress_level,
                "time": c.checkin_date.strftime("%Y-%m-%d %H:%M")
            } for c in recent_checkins
        ],
        "team_stability": team_analytics[:15] # Limit to top 15 for UI clarity
    }

@router.get("/manager-heatmap")
async def get_manager_heatmap(
    manager: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Heatmap data for manager's team"""
    team_members = db.query(User).filter(User.manager_id == manager.id).all()
    team_ids = [u.id for u in team_members]
    
    # Mock heatmap data for now (hours of day vs day of week)
    # In a real app, this would be derived from TaskLog entries
    return {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "values": [random.randint(4, 10) for _ in range(5)]
    }

@router.get("/all-employees")
async def list_all_employees(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all employees for both Admin and Manager oversight"""
    if user.role not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to workforce directory")
        
    employees = db.query(User).filter(User.role == "Employee").all()
    return [u.to_dict() for u in employees]
