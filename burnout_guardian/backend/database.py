"""
Database Configuration and Session Management
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from backend.config import settings
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation="500 MB", level=settings.LOG_LEVEL)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    logger.info("Initializing database...")
    
    # Import all models to ensure they're registered
    from backend.models import user_model, feature_model, stability_model, forecast_model, intervention_model, management_model
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Debug: print columns
    if 'behavioral_features' in Base.metadata.tables:
        cols = [c.name for c in Base.metadata.tables['behavioral_features'].columns]
        logger.info(f"Columns in behavioral_features: {cols}")
    
    logger.info("✅ Database initialized successfully")


def drop_db():
    """Drop all tables - USE WITH CAUTION"""
    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✅ All tables dropped")


if __name__ == "__main__":
    """Run database initialization"""
    print("=" * 60)
    print("🗄️  DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    
    init_db()
    
    print()
    print("=" * 60)
    print("✨ Database ready!")
    print("=" * 60)
