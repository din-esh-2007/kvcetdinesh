"""
Seed Database with Admin User
"""
import sys
import os
import traceback
sys.path.insert(0, os.getcwd())

from backend.database import SessionLocal, init_db
from backend.models.user_model import User
from backend.services.auth_service import get_password_hash
from datetime import datetime

def seed():
    try:
        print("🚀 Seeding database...")
        init_db()
        db = SessionLocal()
        
        # Check if admin exists
        print("Checking for existing admin...")
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                employee_id="ADM001",
                email="admin@burnoutguardian.ai",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role="Admin",
                joining_date=datetime.utcnow(),
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created: admin / admin123")
        else:
            print("ℹ️ Admin user already exists")
        
        db.close()
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    seed()
