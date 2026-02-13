"""
Seed Database with Meaningful Stability Data
Populates the database with realistic test users and baseline monitoring data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import uuid

from backend.database import SessionLocal, init_db, drop_db
from backend.models.user_model import User, DailyCheckIn, EmotionCapture
from backend.models.stability_model import StabilityAssessment
from backend.models.forecast_model import BurnoutForecast
from backend.models.intervention_model import Intervention
from backend.models.management_model import Task
from backend.services.auth_service import get_password_hash
from loguru import logger

def np_clip(n, smallest, largest):
    return max(smallest, min(n, largest))

def seed_data():
    db = SessionLocal()
    
    try:
        # 1. Clean existing data
        logger.info("Cleaning ALL existing operational data for fresh high-density simulation...")
        db.query(StabilityAssessment).delete()
        db.query(BurnoutForecast).delete()
        db.query(Intervention).delete()
        db.query(Task).delete()
        db.query(DailyCheckIn).delete()
        db.query(EmotionCapture).delete()
        db.query(User).delete()
        db.commit()

        # 2. Create Tactical Personnel Hub
        logger.info("Provisioning high-fidelity workforce fleet (200 Assets, 10 Managers)...")
        
        # Admin
        admin = User(
            username="admin",
            full_name="Strategic Administrator",
            email="admin@burnoutguardian.ai",
            hashed_password=get_password_hash("admin123"),
            role="Admin",
            employee_id="ADM-001",
            is_active=True
        )
        db.add(admin)

        # Provision 10 Managers
        managers = []
        for i in range(1, 11):
            mgr = User(
                username=f"manager.{i}",
                full_name=f"Tactical Manager {i}",
                email=f"manager.{i}@burnoutguardian.ai",
                hashed_password=get_password_hash("manager123"),
                role="Manager",
                employee_id=f"MGR-{100+i:03d}",
                is_active=True
            )
            managers.append(mgr)
            db.add(mgr)
        
        db.commit() # Flush for IDs

        # Provision 200 Employees
        employees = []
        depts = ["Engineering", "Product", "Design", "Marketing", "Sales", "Security"]
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson"]

        for i in range(1, 201):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            fullName = f"{fname} {lname} {i}" # Ensure unique full name for traceability
            username = f"{fname.lower()}.{lname.lower()}.{i}"
            
            emp = User(
                username=username,
                full_name=fullName,
                email=f"{username}@company.ai",
                hashed_password=get_password_hash("emp123"),
                role="Employee",
                employee_id=f"EMP-{500+i:03d}",
                manager_id=random.choice(managers).id,
                is_active=True,
                department_id=random.choice(depts)
            )
            employees.append(emp)
            db.add(emp)
        
        db.commit()

        # 3. Generate Historical Stability Telemetry (Last 30 Days)
        logger.info("Generating high-density stability telemetry across 200 assets...")
        now = datetime.now()
        
        # Batch processing for efficiency if needed, but for 200*30 it's manageable
        for emp in employees:
            base_stability = random.uniform(0.60, 0.90)
            trend = random.uniform(-0.005, 0.005) 
            
            assessments = []
            for d in range(30, -1, -1):
                date = now - timedelta(days=d)
                noise = random.uniform(-0.08, 0.08)
                stability = np_clip(base_stability + (trend * (30-d)) + noise, 0.25, 1.0)
                risk_prob = np_clip(1.0 - stability + random.uniform(-0.1, 0.1), 0.0, 1.0)
                
                level = "low"
                if risk_prob > 0.85: level = "critical"
                elif risk_prob > 0.70: level = "high"
                elif risk_prob > 0.45: level = "moderate"

                assessments.append(StabilityAssessment(
                    user_id=emp.id,
                    assessment_date=date,
                    stability_index=round(stability, 2),
                    volatility=round(random.uniform(0.05, 0.45), 2),
                    acceleration=round(random.uniform(-0.05, 0.05), 3),
                    risk_probability=round(risk_prob, 2),
                    risk_level=level,
                    top_contributors=["High Task Intensity", "Resource Contention"] if risk_prob > 0.5 else ["Stable Baseline"],
                    behavioral_score=round(stability * 0.85, 2),
                    confidence_score=0.94
                ))
            db.bulk_save_objects(assessments)
                
        # 4. Project Predictive Risk Flux (Next 7 Days)
        logger.info("Hydrating predictive risk models for all active assets...")
        for emp in employees:
            base_risk = random.uniform(0.15, 0.55)
            f_dates = [(now + timedelta(days=d)).isoformat() for d in range(1, 8)]
            f_values = [round(np_clip(base_risk + (d * 0.035 * random.choice([1, -1, 0.5])) + random.uniform(-0.04, 0.04), 0.1, 0.98), 2) for d in range(1, 8)]
            peak_val = max(f_values)
            peak_idx = f_values.index(peak_val)

            forecast = BurnoutForecast(
                user_id=emp.id,
                forecast_date=now,
                horizon_days=7,
                forecast_values=f_values,
                forecast_dates=f_dates,
                peak_risk_date=now + timedelta(days=peak_idx + 1),
                peak_risk_probability=peak_val,
                model_type="transformer_ensemble",
                confidence_score=round(random.uniform(0.85, 0.96), 2)
            )
            db.add(forecast)

        # 5. Seed Wellness Logs (Last 7 Days for 25% of workforce)
        logger.info("Simulating partial personnel wellness self-reporting...")
        for emp in employees[::4]: # 25% sample
            for d in range(7):
                db.add(DailyCheckIn(
                    user_id=emp.id,
                    checkin_date=now - timedelta(days=d),
                    sleep_hours=round(random.uniform(5.0, 9.0), 1),
                    mood_rating=random.randint(3, 10),
                    stress_level=random.randint(1, 8),
                    energy_level=random.randint(2, 9),
                    work_hours_planned=random.randint(5, 12),
                    notes="Self-reported via mobile terminal."
                ))

        db.commit()
        logger.info(f"✅ SUCCESSFULLY PURGED & RE-SEEDED: 200 Personnel Assets, 10 Tactical Managers.")

    except Exception as e:
        logger.error(f"❌ TACTICAL SEED FAILURE: {e}")
        db.rollback()
    finally:
        db.close()

def np_clip(val, min_val, max_val):
    return max(min_val, min(max_val, val))

if __name__ == "__main__":
    seed_data()
