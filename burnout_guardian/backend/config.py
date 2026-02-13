"""
Configuration Management
Centralized configuration for the Burnout Guardian system
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Burnout & Focus Guardian"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.abspath('burnout_guardian_v2.db')}"
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ML Models
    MODEL_PATH: str = "models/trained"
    ISOLATION_FOREST_CONTAMINATION: float = 0.1
    STABILITY_WINDOW_DAYS: int = 7
    
    # Risk Thresholds
    RISK_THRESHOLD_BUFFER: float = 0.60
    RISK_THRESHOLD_REDISTRIBUTE: float = 0.75
    RISK_THRESHOLD_ALERT: float = 0.85
    
    # Intervention Parameters
    BUFFER_DURATION_MINUTES: int = 45
    MAX_DAILY_INTERVENTIONS: int = 3
    
    # Forecasting
    FORECAST_HORIZON_DAYS: int = 7
    PROPHET_CHANGEPOINT_PRIOR: float = 0.05
    LSTM_SEQUENCE_LENGTH: int = 14
    LSTM_HIDDEN_SIZE: int = 64
    
    # Computer Vision
    CV_ENABLED: bool = True
    CV_CAPTURE_INTERVAL_MINUTES: int = 30
    DEEPFACE_BACKEND: str = "opencv"
    DEEPFACE_MODEL: str = "Facenet"
    
    # Daily Check-In
    CHECKIN_REMINDER_HOUR: int = 9  # 9 AM
    CHECKIN_WEIGHT_BEHAVIORAL: float = 0.7
    CHECKIN_WEIGHT_SELFREPORT: float = 0.3
    
    # Streaming
    STREAM_INTERVAL_MINUTES: int = 5
    STREAM_BATCH_SIZE: int = 50
    
    # Google Calendar
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_CALENDAR_TOKEN_FILE: str = "token.json"
    GOOGLE_CALENDAR_SCOPES: list = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    # Report Generation
    REPORT_OUTPUT_DIR: str = "reports"
    REPORT_LOGO_PATH: Optional[str] = None
    
    # Dataset Generation
    DATASET_NUM_EMPLOYEES: int = 200
    DATASET_NUM_DAYS: int = 120
    DATASET_OUTPUT_PATH: str = "data/synthetic_dataset.csv"
    
    # Feature Engineering Weights
    WEIGHT_INSTABILITY: float = 0.4
    WEIGHT_RECOVERY_DEFICIT: float = 0.3
    WEIGHT_VOLATILITY: float = 0.2
    WEIGHT_ERROR_RATE: float = 0.1
    
    # Reinforcement Learning
    RL_LEARNING_RATE: float = 0.01
    RL_DISCOUNT_FACTOR: float = 0.95
    RL_EXPLORATION_RATE: float = 0.1
    
    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "demo@burnoutguardian.ai"
    SMTP_PASSWORD: str = "strong-password-here"
    SMTP_FROM: str = "operations@burnoutguardian.ai"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/burnout_guardian.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Create necessary directories
def create_directories():
    """Create required directories if they don't exist"""
    directories = [
        "data",
        "reports",
        "logs",
        "models/trained",
        ".cache"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize directories on import
create_directories()
