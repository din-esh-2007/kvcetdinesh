"""
Main FastAPI Application
Burnout & Focus Guardian Backend
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.config import settings
from backend.database import get_db, init_db
from loguru import logger

# Import API routes
from backend.api import auth_routes, admin_routes, task_routes, monitoring_routes, reporting_routes


import asyncio

async def real_time_processing_loop():
    """Background loop to process stability data every 5 minutes"""
    while True:
        try:
            logger.info("🔄 Running autonomous stability analysis loop...")
            # This would call the various AI services:
            # 1. Update Features
            # 2. Detect Instability
            # 3. Forecast Collapse
            # 4. Trigger Intervention
            
            # For demo purposes, we log the cycle
            await asyncio.sleep(60 * 5) # 5 minutes
        except Exception as e:
            logger.error(f"❌ Error in real-time loop: {e}")
            await asyncio.sleep(60) # Wait a minute before retry

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    logger.info("🚀 Starting Burnout Guardian...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Start Real-time loop
    loop_task = asyncio.create_task(real_time_processing_loop())
    
    yield
    
    # Clean up
    loop_task.cancel()
    logger.info("👋 Shutting down Burnout Guardian...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-Time Autonomous Human Stability Control System",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from fastapi.staticfiles import StaticFiles
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Include Routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(task_routes.router)
app.include_router(monitoring_routes.router)
app.include_router(reporting_routes.router)

from backend.models.user_model import User
from backend.services.auth_service import get_current_user

@app.get("/api/analytics/stability/current")
async def get_current_stability(
    current_user: User = Depends(get_current_user),
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get stability for logged in user"""
    try:
        from backend.models.stability_model import StabilityAssessment
        from sqlalchemy import and_
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        assessments = db.query(StabilityAssessment).filter(
            and_(
                StabilityAssessment.user_id == current_user.id,
                StabilityAssessment.assessment_date >= start_date
            )
        ).order_by(StabilityAssessment.assessment_date.desc()).all()
        
        if not assessments:
            return {
                "user_id": current_user.id,
                "message": "No stability data found",
                "latest_assessment": {
                    "stability_index": 0.75,
                    "volatility": 0.2,
                    "risk_probability": 0.25,
                    "risk_level": "low",
                    "top_contributors": []
                },
                "history": []
            }
        
        latest = assessments[0]
        
        return {
            "user_id": current_user.id,
            "latest_assessment": {
                "date": latest.assessment_date.isoformat(),
                "stability_index": latest.stability_index,
                "volatility": latest.volatility,
                "risk_probability": latest.risk_probability,
                "risk_level": latest.risk_level,
                "top_contributors": latest.top_contributors
            },
            "history": [
                {
                    "date": a.assessment_date.isoformat(),
                    "stability_index": a.stability_index,
                    "risk_probability": a.risk_probability,
                    "risk_level": a.risk_level
                }
                for a in assessments
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching stability data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/forecast/current")
async def get_current_forecast(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get forecast for logged in user"""
    try:
        from backend.models.forecast_model import BurnoutForecast
        
        forecast = db.query(BurnoutForecast).filter(
            BurnoutForecast.user_id == current_user.id
        ).order_by(BurnoutForecast.forecast_date.desc()).first()
        
        if not forecast:
            return {
                "user_id": current_user.id,
                "message": "No forecast data available",
                "forecast": None
            }
        
        return {
            "user_id": current_user.id,
            "forecast_date": forecast.forecast_date.isoformat(),
            "horizon_days": forecast.horizon_days,
            "peak_risk_date": forecast.peak_risk_date.isoformat() if forecast.peak_risk_date else None,
            "peak_risk_probability": forecast.peak_risk_probability,
            "forecast_values": forecast.forecast_values,
            "forecast_dates": forecast.forecast_dates,
            "model_type": forecast.model_type,
            "confidence_score": forecast.confidence_score
        }
        
    except Exception as e:
        logger.error(f"Error fetching forecast data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# Root endpoint - serve frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    try:
        with open("frontend/dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Burnout Guardian</title></head>
            <body style="font-family: Arial; padding: 40px; background: #0a0e27; color: #fff;">
                <h1>🧠 Burnout & Focus Guardian</h1>
                <h2>Real-Time Autonomous Human Stability Control System</h2>
                <p>System Status: <span style="color: #00ff88;">ONLINE</span></p>
                <hr>
                <h3>API Endpoints:</h3>
                <ul>
                    <li><a href="/docs" style="color: #00d4ff;">/docs</a> - Interactive API Documentation</li>
                    <li><a href="/health" style="color: #00d4ff;">/health</a> - Health Check</li>
                    <li><a href="/api/demo/generate" style="color: #00d4ff;">/api/demo/generate</a> - Generate Demo Data</li>
                </ul>
            </body>
        </html>
        """)


# Demo data generation endpoint
@app.get("/api/demo/generate")
async def generate_demo_data(db: Session = Depends(get_db)):
    """Generate demo data for testing"""
    try:
        from backend.dataset_generator import SyntheticDatasetGenerator
        
        logger.info("Generating demo dataset...")
        
        generator = SyntheticDatasetGenerator(
            num_employees=10,  # Smaller for demo
            num_days=30
        )
        
        df = generator.generate_dataset()
        generator.save_dataset(df, "data/demo_dataset.csv")
        
        return {
            "status": "success",
            "message": "Demo dataset generated",
            "rows": len(df),
            "employees": df['employee_id'].nunique(),
            "file": "data/demo_dataset.csv"
        }
        
    except Exception as e:
        logger.error(f"Demo data generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoint - get user stability
@app.get("/api/analytics/stability/{user_id}")
async def get_user_stability(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get user stability metrics"""
    try:
        from backend.models.stability_model import StabilityAssessment
        from sqlalchemy import and_
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        assessments = db.query(StabilityAssessment).filter(
            and_(
                StabilityAssessment.user_id == user_id,
                StabilityAssessment.assessment_date >= start_date
            )
        ).order_by(StabilityAssessment.assessment_date.desc()).all()
        
        if not assessments:
            return {
                "user_id": user_id,
                "message": "No stability data found",
                "assessments": []
            }
        
        latest = assessments[0]
        
        return {
            "user_id": user_id,
            "latest_assessment": {
                "date": latest.assessment_date.isoformat(),
                "stability_index": latest.stability_index,
                "volatility": latest.volatility,
                "risk_probability": latest.risk_probability,
                "risk_level": latest.risk_level,
                "top_contributors": latest.top_contributors
            },
            "history": [
                {
                    "date": a.assessment_date.isoformat(),
                    "stability_index": a.stability_index,
                    "risk_probability": a.risk_probability,
                    "risk_level": a.risk_level
                }
                for a in assessments
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching stability data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Forecast endpoint
@app.get("/api/analytics/forecast/{user_id}")
async def get_user_forecast(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user burnout forecast"""
    try:
        from backend.models.forecast_model import BurnoutForecast
        
        forecast = db.query(BurnoutForecast).filter(
            BurnoutForecast.user_id == user_id
        ).order_by(BurnoutForecast.forecast_date.desc()).first()
        
        if not forecast:
            return {
                "user_id": user_id,
                "message": "No forecast data found"
            }
        
        return forecast.to_dict()
        
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Intervention history endpoint
@app.get("/api/interventions/history/{user_id}")
async def get_intervention_history(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get intervention history"""
    try:
        from backend.models.intervention_model import Intervention
        
        interventions = db.query(Intervention).filter(
            Intervention.user_id == user_id
        ).order_by(Intervention.intervention_date.desc()).limit(limit).all()
        
        return {
            "user_id": user_id,
            "interventions": [i.to_dict() for i in interventions]
        }
        
    except Exception as e:
        logger.error(f"Error fetching interventions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System stats endpoint
@app.get("/api/system/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system-wide statistics"""
    try:
        from backend.models.user_model import User
        from backend.models.stability_model import StabilityAssessment
        from backend.models.intervention_model import Intervention
        
        total_users = db.query(User).count()
        total_assessments = db.query(StabilityAssessment).count()
        total_interventions = db.query(Intervention).count()
        
        # High risk users
        from datetime import timedelta
        recent_date = datetime.utcnow() - timedelta(days=1)
        
        high_risk_count = db.query(StabilityAssessment).filter(
            and_(
                StabilityAssessment.assessment_date >= recent_date,
                StabilityAssessment.risk_level.in_(["high", "critical"])
            )
        ).count()
        
        return {
            "total_users": total_users,
            "total_assessments": total_assessments,
            "total_interventions": total_interventions,
            "high_risk_users_24h": high_risk_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount frontend static files
# This must be after all other routes to ensure API calls aren't caught by static file server
app.mount("/", StaticFiles(directory="frontend"), name="frontend")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
