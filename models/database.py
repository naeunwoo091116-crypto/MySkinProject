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
def get_database_url():
    """Get appropriate database URL based on environment"""
    # Check if running on Google App Engine
    if os.getenv('GAE_ENV', '').startswith('standard') or os.getenv('GAE_ENV', '') == 'flex':
        # App Engine environment - use Cloud SQL
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASSWORD', 'myskin123')
        db_name = os.getenv('DB_NAME', 'myskin')
        cloud_sql_connection_name = os.getenv('CLOUD_SQL_CONNECTION_NAME')

        if cloud_sql_connection_name:
            # Unix socket connection for Cloud SQL
            return f'postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{cloud_sql_connection_name}'
        else:
            print("WARNING: CLOUD_SQL_CONNECTION_NAME not set in App Engine environment")
            return None
    else:
        # Local development environment
        return os.getenv('DATABASE_URL', 'postgresql://postgres:myskin123@127.0.0.1:5432/myskin')

try:
    # Try to get database URL
    DATABASE_URL = get_database_url()

    if DATABASE_URL:
        engine = create_engine(DATABASE_URL, echo=True)
        # Force connection check
        with engine.connect() as conn:
            pass
        print(f"[INFO] Connected to database: {DATABASE_URL.split('@')[0]}@***")
    else:
        raise Exception("No database URL configured")

except (ImportError, ModuleNotFoundError, Exception) as e:
    print(f"WARNING: Database connection failed (PostgreSQL): {e}")
    print("INFO: Falling back to SQLite...")
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
    password_hash = Column(String(255), nullable=True)  # 비밀번호 해시
    gender = Column(String(20), nullable=True)          # 성별 (male, female, other)
    last_login_at = Column(DateTime, nullable=True)     # 최근 로그인 일시
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'skin_type': self.skin_type,
            'gender': self.gender,
            'concerns': self.concerns,
            'goals': self.goals,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
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


class ChatHistory(Base):
    """챗봇 상담 내역 테이블"""
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=False)
    image_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'reply': self.reply,
            'image_path': self.image_path,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database tables created successfully!")


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
