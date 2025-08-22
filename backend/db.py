from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, UniqueConstraint, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from settings import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    url = Column(Text, unique=True)
    source = Column(String, index=True)  # e.g., 'lever', 'greenhouse'
    posted_at = Column(DateTime, index=True, default=datetime.utcnow)
    description = Column(Text)
    score = Column(Float, default=0.0)  # relevance score

    __table_args__ = (
        UniqueConstraint('url', name='uq_job_url'),
    )

def init_db():
    Base.metadata.create_all(bind=engine)

def upsert_job(session, job_data):
    """Insert or update a job in the database."""
    existing = session.query(Job).filter(Job.url == job_data["url"]).first()
    if existing:
        for field, value in job_data.items():
            if hasattr(existing, field):
                setattr(existing, field, value)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    row = Job(**job_data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
