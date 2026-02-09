from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LearningPathRequest(BaseModel):
    user_id: int = Field(..., description="ID de l'utilisateur")
    topic: str = Field(..., description="Sujet d'apprentissage, ex: 'climat'")
    level: str = Field(..., description="Niveau: beginner/intermediate/advanced")
    duration_minutes: int = Field(..., ge=5, le=240, description="Durée de la session")


class LearningPathContent(BaseModel):
    title: str
    summary: str
    steps: list[str]


class CarbonInfo(BaseModel):
    co2_kg: float
    trees_to_fund: float


class LearningPathResponse(BaseModel):
    session_id: int
    content: LearningPathContent
    difficulty_score: Optional[float] = None
    carbon: CarbonInfo


class CarbonSummary(BaseModel):
    user_id: int
    total_sessions: int
    total_co2_kg: float
    total_trees_to_fund: float
    last_session_at: Optional[datetime] = None

