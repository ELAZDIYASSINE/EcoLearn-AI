from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db, init_db
from .models import CarbonMetric, LearningSession, PlantingEvent, User
from .schemas import (
    CarbonInfo,
    CarbonSummary,
    LearningPathRequest,
    LearningPathResponse,
    UserCreate,
    UserRead,
)
from .services.carbon import compute_carbon_for_session, compute_trees_to_fund
from .services.learning import generate_learning_content
from .services.reforest import trigger_reforestation

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}


@app.post("/users", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    user = db.execute(select(User).where(User.email == user_in.email)).scalar_one_or_none()
    if user:
        return user  # idempotent creation by email
    user = User(email=user_in.email, name=user_in.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/learning/path", response_model=LearningPathResponse)
def create_learning_path(
    req: LearningPathRequest,
    db: Session = Depends(get_db),
) -> LearningPathResponse:
    user = db.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content, difficulty_score = generate_learning_content(req)

    session = LearningSession(
        user_id=user.id,
        topic=req.topic,
        level=req.level,
        duration_minutes=req.duration_minutes,
        generated_content="\n".join([content.title, content.summary, *content.steps]),
        difficulty_score=difficulty_score,
    )
    db.add(session)
    db.flush()

    co2_kg = compute_carbon_for_session(req.duration_minutes)
    trees = compute_trees_to_fund(co2_kg)

    metric = CarbonMetric(
        session_id=session.id,
        user_id=user.id,
        co2_kg=co2_kg,
        trees_to_fund=trees,
    )
    db.add(metric)

    # Optionnel : créer un évènement de plantation si on dépasse un certain seuil
    external_id = None
    if trees >= 1:
        external_id = trigger_reforestation(int(trees), co2_kg)
        planting = PlantingEvent(
            provider="reforest_stub",
            trees=int(trees),
            co2_offset_kg=co2_kg,
            external_id=external_id,
        )
        db.add(planting)

    db.commit()
    db.refresh(session)

    carbon_info = CarbonInfo(co2_kg=co2_kg, trees_to_fund=trees)
    return LearningPathResponse(
        session_id=session.id,
        content=content,
        difficulty_score=difficulty_score,
        carbon=carbon_info,
    )


@app.get("/carbon/summary/{user_id}", response_model=CarbonSummary)
def get_carbon_summary(user_id: int, db: Session = Depends(get_db)) -> CarbonSummary:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(
        func.count(CarbonMetric.id),
        func.coalesce(func.sum(CarbonMetric.co2_kg), 0.0),
        func.coalesce(func.sum(CarbonMetric.trees_to_fund), 0.0),
    ).where(CarbonMetric.user_id == user_id)
    total_sessions, total_co2, total_trees = db.execute(stmt).one()

    last_session = (
        db.execute(
            select(LearningSession)
            .where(LearningSession.user_id == user_id)
            .order_by(LearningSession.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )

    return CarbonSummary(
        user_id=user_id,
        total_sessions=int(total_sessions or 0),
        total_co2_kg=float(total_co2 or 0.0),
        total_trees_to_fund=float(total_trees or 0.0),
        last_session_at=last_session.created_at if last_session else None,
    )


@app.get("/")
def root() -> dict:
    return {
        "message": "EcoLearn AI backend",
        "docs_url": "/docs",
    }

