"""
Seed Database with Activity Data
Generates 14 days of Daily Check-ins, Emotion Captures, Stability Assessments, and Interventions.
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.models.user_model import User, DailyCheckIn, EmotionCapture
from backend.models.management_model import Task, TaskLog
from backend.models.stability_model import StabilityAssessment
from backend.models.intervention_model import Intervention

def seed_activity():
    db = SessionLocal()
    try:
        print("📊 Seeding historical activity data...")
        
        # Get all Employees
        employees = db.query(User).filter(User.role == "Employee").all()
        if not employees:
            print("❌ No employees found. Please run seed_data.py first.")
            return

        total_checkins = 0
        total_emotions = 0
        total_tasks = 0
        total_assessments = 0
        total_interventions = 0

        # Generate data for the last 14 days for more history
        for day_offset in range(14, -1, -1):
            checkin_date = datetime.now() - timedelta(days=day_offset)
            
            for emp in employees:
                # 1. Daily Check-in (80% participation rate)
                has_checkin = False
                mood = 7
                stress = 3
                if random.random() < 0.8:
                    is_midweek = checkin_date.weekday() in [1, 2, 3] 
                    mood = random.randint(4, 9) if not is_midweek else random.randint(3, 7)
                    stress = random.randint(2, 6) if not is_midweek else random.randint(5, 9)
                    
                    checkin = DailyCheckIn(
                        user_id=emp.id,
                        checkin_date=checkin_date,
                        sleep_hours=random.uniform(5.5, 8.5) if not is_midweek else random.uniform(4.5, 7.5),
                        work_hours_planned=random.uniform(7, 9),
                        mood_rating=mood,
                        stress_level=stress,
                        energy_level=random.randint(5, 10) if not is_midweek else random.randint(3, 8),
                        caffeine_intake=random.randint(0, 4),
                        exercise_minutes=random.choice([0, 0, 15, 30, 45, 60]),
                        notes="Operational status: Nominal." if stress < 6 else "Alert: Workload exceeding stability thresholds."
                    )
                    db.add(checkin)
                    total_checkins += 1
                    has_checkin = True

                # 2. Emotion Captures
                stability_sum = 0
                capture_count = random.randint(2, 4)
                for _ in range(capture_count):
                    s_idx = random.uniform(0.5, 0.95)
                    stability_sum += s_idx
                    ec = EmotionCapture(
                        user_id=emp.id,
                        captured_at=checkin_date - timedelta(hours=random.randint(1, 10)),
                        happy=random.uniform(0, 0.8),
                        sad=random.uniform(0, 0.4),
                        angry=random.uniform(0, 0.3),
                        neutral=random.uniform(0.1, 0.9),
                        stress_proxy=random.uniform(0, 0.6),
                        emotional_stability_index=s_idx,
                        confidence_score=random.uniform(0.8, 0.99)
                    )
                    db.add(ec)
                    total_emotions += 1
                
                avg_emo_stability = stability_sum / capture_count if capture_count > 0 else 0.7

                # 3. Stability Assessment (Generated daily)
                risk_prob = (stress / 10.0) * 0.7 + (1 - avg_emo_stability) * 0.3
                risk_level = "low"
                if risk_prob > 0.8: risk_level = "critical"
                elif risk_prob > 0.6: risk_level = "high"
                elif risk_prob > 0.4: risk_level = "moderate"

                assessment = StabilityAssessment(
                    user_id=emp.id,
                    assessment_date=checkin_date,
                    stability_index=1.0 - risk_prob,
                    volatility=random.uniform(0.1, 0.4) if risk_level == "low" else random.uniform(0.5, 0.9),
                    acceleration=random.uniform(-0.1, 0.1),
                    risk_probability=risk_prob,
                    risk_level=risk_level,
                    top_contributors=["Workload Volatility", "Sleep Deprivation"] if stress > 6 else ["Stable Routine"],
                    is_anomaly=1 if risk_prob > 0.85 else 0,
                    hybrid_score=random.uniform(60, 95)
                )
                db.add(assessment)
                total_assessments += 1

                # 4. Trigger Autonomous Intervention if risk is High/Critical
                if risk_level in ["high", "critical"] and random.random() < 0.7:
                    i_type = random.choice(["buffer", "redistribute", "alert"])
                    intervention = Intervention(
                        user_id=emp.id,
                        intervention_date=checkin_date + timedelta(hours=1),
                        intervention_type=i_type,
                        trigger_risk_level=risk_level,
                        trigger_risk_probability=risk_prob,
                        action_description=f"Automatic {i_type} to mitigate {risk_level} collapse risk.",
                        status="executed",
                        is_autonomous=True,
                        effectiveness_score=random.uniform(0.6, 0.9)
                    )
                    db.add(intervention)
                    total_interventions += 1

        # 5. Tasks and Logs (2 tasks per employee)
        task_titles = [
            "Q1 Performance Analysis", "Security Patch Update", "Client Onboarding UI",
            "Database Migration", "API Documentation Review", "Internal Dashboard Refactor",
            "Cloud Infrastructure Optimization", "Employee Feedback Processing"
        ]

        for emp in employees:
            for i in range(2):
                expected = random.randint(4, 16)
                task = Task(
                    title=f"{random.choice(task_titles)} - Phase {i+1}",
                    description="Standard operational sequence for human resource optimization.",
                    manager_id=emp.manager_id if emp.manager_id else "SYSTEM",
                    assigned_to_id=emp.id,
                    expected_hours=expected,
                    actual_hours=random.uniform(1, expected + 2),
                    deadline=datetime.now() + timedelta(days=random.randint(1, 14)),
                    priority=random.choice(["Medium", "High", "Critical"]),
                    status=random.choice(["In Progress", "Completed", "Pending"])
                )
                db.add(task)
                total_tasks += 1

        db.commit()
        print(f"✅ Generated {total_checkins} check-ins.")
        print(f"✅ Generated {total_emotions} emotion captures.")
        print(f"✅ Generated {total_assessments} stability assessments.")
        print(f"✅ Generated {total_interventions} interventions.")
        print(f"✅ Generated {total_tasks} task assignments.")
        print("✨ Activity & AI Intelligence seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding activity: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_activity()
