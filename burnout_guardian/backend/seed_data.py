"""
Seed Database with Managers and Employees
Generates 10 Managers and 100 Employees with realistic profiles
"""

import sys
import os
import random
import uuid
from datetime import datetime, timedelta

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models.user_model import User
from backend.models.management_model import Department
from backend.services.auth_service import get_password_hash

# Initialize Database
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding database...")
        
        # 1. Create Departments
        dept_names = ['IT & Infrastructure', 'Human Resources', 'Engineering', 'Sales & Marketing', 
                      'Finance', 'Legal', 'Customer Success', 'Product Management', 'Research', 'Operations']
        
        departments = []
        for name in dept_names:
            dept = db.query(Department).filter(Department.name == name).first()
            if not dept:
                dept = Department(name=name, description=f"The {name} department focusing on organizational excellence.")
                db.add(dept)
                db.flush() # To get ID
            departments.append(dept)
        
        print(f"✅ Created {len(departments)} departments.")

        # Lists for random generation
        first_names = ["Arjun", "Deepika", "Vikram", "Ananya", "Rohan", "Priya", "Karan", "Sanya", "Rahul", "Neha", 
                       "Siddharth", "Ishita", "Aditya", "Riya", "Varun", "Meera", "Kabir", "Zara", "Aman", "Tanya"]
        last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Kapoor", "Joshi", "Patel", "Reddy", "Nair", "Iyer", 
                      "Singh", "Kaur", "Dutta", "Bose", "Das", "Menon", "Chaudhary", "Khan", "Desai", "Rao"]
        genders = ["Male", "Female", "Other"]
        emp_types = ["Full-Time", "Part-Time", "Contract"]
        cities = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune"]

        # 2. Create Managers (10)
        managers = []
        password_hash = get_password_hash("password123")
        
        for i in range(1, 11):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            full_name = f"{fname} {lname}"
            username = f"manager{i:02d}"
            emp_id = f"MGR{100 + i}"
            email = f"{username}@burnoutguardian.ai"
            
            # Realistic DOB (30-50 years old)
            age_days = random.randint(30*365, 50*365)
            dob = datetime.now() - timedelta(days=age_days)
            
            # Joining Date (1-5 years ago)
            join_days = random.randint(365, 5*365)
            join_date = datetime.now() - timedelta(days=join_days)

            user = db.query(User).filter(User.username == username).first()
            if not user:
                user = User(
                    username=username,
                    employee_id=emp_id,
                    email=email,
                    full_name=full_name,
                    hashed_password=password_hash,
                    mobile_number=f"+91 98765{i:05d}",
                    gender=random.choice(genders),
                    address=f"{random.randint(10, 500)}, High Street, {random.choice(cities)}",
                    dob=dob,
                    employment_type="Full-Time",
                    emergency_contact=f"Relative: +91 99999{i:05d}",
                    joining_date=join_date,
                    role="Manager",
                    department_id=random.choice(departments).id
                )
                db.add(user)
                db.flush()
            managers.append(user)

        print(f"✅ Created {len(managers)} managers.")

        # 3. Create Employees (100)
        for i in range(1, 101):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            full_name = f"{fname} {lname}"
            username = f"emp{i:03d}"
            emp_id = f"EMP{500 + i}"
            email = f"{username}@burnoutguardian.ai"
            
            # Realistic DOB (18-35 years old)
            # 18 years = 18 * 365 = 6570 days
            age_days = random.randint(18*365 + 10, 35*365)
            dob = datetime.now() - timedelta(days=age_days)
            
            # Joining Date (1 month to 2 years ago)
            join_days = random.randint(30, 2*365)
            join_date = datetime.now() - timedelta(days=join_days)

            user = db.query(User).filter(User.username == username).first()
            if not user:
                manager = random.choice(managers)
                user = User(
                    username=username,
                    employee_id=emp_id,
                    email=email,
                    full_name=full_name,
                    hashed_password=password_hash,
                    mobile_number=f"+91 88888{i:05d}",
                    gender=random.choice(genders),
                    address=f"{random.randint(1, 1000)}, Avenue Road, {random.choice(cities)}",
                    dob=dob,
                    employment_type=random.choice(emp_types),
                    emergency_contact=f"Friend: +91 77777{i:05d}",
                    joining_date=join_date,
                    role="Employee",
                    department_id=manager.department_id,
                    manager_id=manager.id
                )
                db.add(user)

        db.commit()
        print(f"✅ Created 100 employees.")
        print("✨ Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
