# 🧠 Burnout & Focus Guardian

## Real-Time Autonomous Human Stability Control System

A production-ready AI system that passively monitors workplace behavioral metadata, detects instability patterns, forecasts burnout windows, and executes autonomous stabilization interventions.

## 🎯 Core Features

- **Passive Behavioral Monitoring**: Tracks workplace metadata without content scraping
- **ML-Powered Detection**: Real-time instability detection using Isolation Forest & Bayesian change-point detection
- **Predictive Forecasting**: 7-day burnout probability forecasting using Prophet & LSTM
- **Autonomous Interventions**: Automatic calendar buffer insertion and workload redistribution
- **Computer Vision Integration**: Opt-in emotion detection using DeepFace
- **Daily Check-In System**: Hybrid behavioral + self-reported data fusion
- **Reinforcement Learning**: Adaptive intervention optimization based on outcomes
- **Explainable Reports**: PDF reports with actionable insights

## 🏗️ Architecture

```
burnout_guardian/
├── backend/              # FastAPI backend
│   ├── models/          # Database models
│   ├── services/        # Core business logic
│   ├── api/             # REST API routes
│   ├── streaming/       # Real-time event processing
│   └── utils/           # Helper utilities
├── frontend/            # Premium UI dashboard
├── data/                # Generated datasets
└── reports/             # Generated PDF reports
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Node.js 16+ (for frontend)

### Installation

1. **Clone and navigate to project**
```bash
cd burnout_guardian
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**
```bash
# Create database
createdb burnout_guardian

# Update .env with your database credentials
```

4. **Generate synthetic dataset**
```bash
python backend/dataset_generator.py
```

5. **Run database migrations**
```bash
python backend/database.py
```

6. **Start Redis**
```bash
redis-server
```

7. **Start the backend**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Access the application**
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Manager Dashboard: http://localhost:8000/manager
- Leadership Dashboard: http://localhost:8000/leadership

## 🐳 Docker Deployment

```bash
docker build -t burnout-guardian .
docker run -p 8000:8000 burnout-guardian
```

## 📊 System Components

### 1. Dataset Generation
- 200 employees × 120 days = 24,000 data points
- 40+ behavioral signals per employee per day
- Realistic burnout progression patterns

### 2. Feature Engineering
- Meeting density index
- Task switching rate
- Recovery gap duration
- Deadline compression ratio
- Volatility acceleration

### 3. Instability Detection
- 7-day rolling baseline
- Isolation Forest anomaly detection
- Bayesian change-point detection
- Multi-signal risk scoring

### 4. Forecasting Engine
- Prophet time-series forecasting
- LSTM multi-step prediction
- Collapse probability curves

### 5. Decision Engine
- Risk threshold-based interventions
- Automatic calendar buffer insertion
- Manager alert generation
- Workload redistribution suggestions

### 6. Reinforcement Learning
- Post-intervention outcome tracking
- Adaptive threshold adjustment
- Personalized resilience profiling

### 7. Computer Vision
- Webcam-based emotion detection
- DeepFace emotion classification
- Emotional stability index
- Privacy-first opt-in system

### 8. Daily Check-In
- Sleep hours tracking
- Mood rating (1-10)
- Self-reported work hours
- Caffeine intake monitoring

## 🎨 Frontend Features

- **Premium Futuristic UI**: Deep navy + glassmorphism + teal accents
- **Real-Time Stability Wave**: Animated stability visualization
- **Collapse Probability Curve**: 7-day forecast visualization
- **Volatility Radar**: Multi-dimensional risk assessment
- **Action Log**: Intervention history timeline
- **CV Emotion Display**: Real-time emotion tracking
- **Manager Heatmap**: Team-wide risk visualization
- **Leadership SDG Dashboard**: Organizational sustainability metrics

## 🔒 Security & Ethics

- **Metadata Only**: No email/message content scraping
- **Explicit Consent**: Opt-in for CV emotion detection
- **Audit Logs**: Complete intervention tracking
- **Override Control**: Manual intervention disable
- **Privacy First**: GDPR-compliant data handling

## 📈 API Endpoints

### User Management
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/users/me` - Get current user profile

### Analytics
- `GET /api/analytics/stability/{user_id}` - Get stability metrics
- `GET /api/analytics/forecast/{user_id}` - Get burnout forecast
- `GET /api/analytics/team` - Team-wide analytics

### Interventions
- `POST /api/interventions/execute` - Trigger intervention
- `GET /api/interventions/history/{user_id}` - Intervention history
- `POST /api/interventions/feedback` - Log intervention outcome

### Computer Vision
- `POST /api/cv/capture` - Capture emotion snapshot
- `GET /api/cv/history/{user_id}` - Emotion history
- `POST /api/cv/opt-in` - Enable CV tracking

### Daily Check-In
- `POST /api/checkin/submit` - Submit daily check-in
- `GET /api/checkin/history/{user_id}` - Check-in history

## 🧪 Demo Mode

Run streaming simulation for hackathon demo:

```bash
python backend/streaming/event_listener.py --demo-mode
```

This simulates 200 employees over 5 minutes with accelerated time.

## 📊 Sample Output

### Stability Report
```json
{
  "stability_index": 0.72,
  "volatility": 0.34,
  "acceleration": 0.12,
  "risk_probability": 0.68,
  "top_contributors": [
    "meeting_density",
    "recovery_deficit",
    "task_switching_rate"
  ],
  "forecast_7d": [0.68, 0.71, 0.75, 0.78, 0.82, 0.85, 0.88],
  "recommended_actions": [
    "Insert 45-min focus buffer",
    "Reduce meeting load by 30%",
    "Extend recovery window"
  ]
}
```

## 🏆 Hackathon Positioning

**Real-Time Human Stability Controller**

This system autonomously:
- Detects instability patterns before collapse
- Forecasts tipping-point windows with 7-day horizon
- Executes stabilizing interventions automatically
- Learns from outcomes to optimize future actions
- Integrates behavioral + emotional intelligence

**Alignment with UN SDGs:**
- SDG 3: Good Health and Well-being
- SDG 8: Decent Work and Economic Growth

## 📝 License

MIT License - Built for human sustainability

## 👥 Contributors

Built with ❤️ for healthier workplaces
