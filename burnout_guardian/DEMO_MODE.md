# 🚀 QUICK DEMO MODE - No Database Required

This guide helps you run the Burnout Guardian system immediately without setting up PostgreSQL.

## Quick Start (5 minutes)

### 1. Install Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install minimal dependencies
pip install fastapi uvicorn pandas numpy scikit-learn
```

### 2. Generate Demo Dataset

```powershell
python backend/dataset_generator.py
```

This creates `data/synthetic_dataset.csv` with 24,000 rows of realistic behavioral data.

### 3. Start Demo Server

```powershell
# Run the simplified demo server
uvicorn backend.main:app --reload --port 8000
```

### 4. Access the Application

Open your browser to:
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Demo Data**: http://localhost:8000/api/demo/generate

## What Works in Demo Mode

✅ **Dataset Generation**
- 200 employees × 120 days
- 40+ behavioral signals
- Realistic burnout patterns

✅ **API Endpoints**
- Health check
- System stats
- Demo data generation

✅ **Frontend Dashboard**
- Premium futuristic UI
- Interactive charts (Chart.js)
- Responsive design

## What Requires Full Setup

❌ **Database Features** (requires PostgreSQL)
- User authentication
- Stability assessments storage
- Intervention tracking
- Forecast persistence

❌ **ML Services** (requires full dependencies)
- Real-time instability detection
- Prophet/LSTM forecasting
- Computer vision emotion detection

❌ **Autonomous Interventions** (requires calendar integration)
- Google Calendar OAuth
- Automatic buffer insertion
- Email/Slack notifications

## Next Steps

To enable full functionality:

1. **Install PostgreSQL**
   ```powershell
   # Download from: https://www.postgresql.org/download/windows/
   # Create database: burnout_guardian
   ```

2. **Install All Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set Up Environment**
   ```powershell
   # Copy .env.example to .env
   # Update DATABASE_URL with your PostgreSQL credentials
   ```

4. **Initialize Database**
   ```powershell
   python backend/database.py
   ```

5. **Run Full System**
   ```powershell
   .\start.ps1
   ```

## Demo Scenarios

### Scenario 1: View Synthetic Dataset
```powershell
# Generate and view the dataset
python backend/dataset_generator.py

# Open data/synthetic_dataset.csv in Excel
# Explore the 40+ behavioral signals
```

### Scenario 2: Test ML Detection (Standalone)
```python
# Run in Python REPL
from backend.dataset_generator import SyntheticDatasetGenerator
import pandas as pd

# Generate small dataset
gen = SyntheticDatasetGenerator(num_employees=10, num_days=30)
df = gen.generate_dataset()

# View high-risk employees
high_risk = df[df['collapse_probability'] > 0.7]
print(f"High risk rows: {len(high_risk)}")
print(high_risk[['employee_id', 'day_index', 'collapse_probability', 'instability_index']])
```

### Scenario 3: Explore API
```powershell
# Start server
uvicorn backend.main:app --reload

# Visit http://localhost:8000/docs
# Try the interactive API documentation
```

## Troubleshooting

### Issue: "Module not found"
```powershell
# Make sure you're in the virtual environment
.\venv\Scripts\Activate.ps1

# Install missing package
pip install <package-name>
```

### Issue: "Port 8000 already in use"
```powershell
# Use a different port
uvicorn backend.main:app --reload --port 8080
```

### Issue: "Cannot find dataset_generator.py"
```powershell
# Make sure you're in the project root
cd c:\Users\dines\Downloads\kvcet\burnout_guardian

# Check file exists
ls backend\dataset_generator.py
```

## Demo Presentation Tips

1. **Show the Dataset**
   - Open `data/synthetic_dataset.csv`
   - Highlight the 40+ features
   - Show collapse probability distribution

2. **Show the Dashboard**
   - Navigate to http://localhost:8000
   - Demonstrate the premium UI
   - Show the interactive charts

3. **Show the Architecture**
   - Open `PROJECT_SUMMARY.md`
   - Walk through the system diagram
   - Explain the ML pipeline

4. **Show the Code**
   - Open `backend/services/instability_detection.py`
   - Explain Isolation Forest + Bayesian detection
   - Show the decision engine logic

## Performance Notes

- Dataset generation: ~30 seconds for 200 employees
- API response time: <100ms
- Frontend load time: <1 second
- Chart rendering: Real-time

## Resources

- **Documentation**: README.md
- **Architecture**: PROJECT_SUMMARY.md
- **API Docs**: http://localhost:8000/docs (when running)
- **Code**: All files in `backend/` and `frontend/`

---

**Ready to impress! 🚀**
