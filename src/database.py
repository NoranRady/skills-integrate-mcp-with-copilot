"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Database configuration
database_dir = Path(__file__).parent.parent / "data"
database_dir.mkdir(exist_ok=True)
database_url = f"sqlite:///{database_dir}/mergington.db"

# Create engine with connection pooling
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database with all tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)
