"""
SQLAlchemy Database Models for MySkin Project
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
# Database setup
try:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:myskin123@localhost:5432/myskin')
    engine = create_engine(DATABASE_URL, echo=True)
    # Force connection check to fail early if driver missing
    with engine.connect() as conn:
        pass
except (ImportError, ModuleNotFoundError, Exception) as e:
    print(f"⚠️ Database connection failed (PostgreSQL): {e}")
    print("🔄 Falling back to SQLite...")
    DATABASE_URL = "sqlite:///./myskin.db"
    engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """사용자 프로필 테이블"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100))
    skin_type = Column(String(50))
    concerns = Column(JSON)  # ["주름", "색소침착", "모공"]
    goals = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'skin_type': self.skin_type,
            'concerns': self.concerns,
            'goals': self.goals,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AnalysisHistory(Base):
    """피부 분석 히스토리 테이블"""
    __tablename__ = 'analysis_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    overall_score = Column(Integer)
    regions = Column(JSON, nullable=False)  # 전체 regions 데이터
    recommendation = Column(JSON)  # LED 추천 데이터
    course_name = Column(String(100), default='AI 정밀 분석')

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'overall_score': self.overall_score,
            'regions': self.regions,
            'recommendation': self.recommendation,
            'course_name': self.course_name
        }


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == '__main__':
    # Run this file directly to create tables
    print("Creating database tables...")
    init_db()
