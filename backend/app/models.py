from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("LearningSession", back_populates="user")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    generated_content = Column(Text, nullable=False)
    difficulty_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")
    carbon_metric = relationship(
        "CarbonMetric", back_populates="session", uselist=False
    )


class CarbonMetric(Base):
    __tablename__ = "carbon_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    co2_kg = Column(Float, nullable=False)
    trees_to_fund = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("LearningSession", back_populates="carbon_metric")
    user = relationship("User")


class PlantingEvent(Base):
    __tablename__ = "planting_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(100), nullable=False)
    trees = Column(Integer, nullable=False)
    co2_offset_kg = Column(Float, nullable=False)
    external_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

