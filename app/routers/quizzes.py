from __future__ import annotations

from typing import Dict, List
from datetime import date
from uuid import uuid4, UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import uuid4

from app.routers.deps import get_authenticated_user, get_db
from app.models.schema import (
    PointWallet,
    PointHistory,
    Location,
    Question,
    Users,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("/today")
def get_today_quiz(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> Dict[str, List[dict]]:
    """Return today's quiz questions for the authenticated user."""

    user_id = user["user_id"]

    db_user = db.query(Users).filter(Users.user_id == user_id).first()
    if not db_user:
        return {"questions": []}

    location = db.query(Location).filter(Location.loc_id == db_user.loc_id).first()
    plan_id = location.plan_id if location else None

    sugarcane_qs = db.query(Question).filter(
        Question.question_type == "Sugarcane"
    ).all()

    role_qs = db.query(Question).filter(
        Question.question_type == "Role",
        Question.role_id == db_user.role_id,
    ).all()

    plan_qs = db.query(Question).filter(
        Question.question_type == "Plan",
        Question.plan_id == plan_id,
    ).all()

    questions = sugarcane_qs + role_qs + plan_qs

    return {
        "questions": [
            {
                "question_id": str(q.question_id),
                "question": q.question_text,
                "options": {
                    "A": q.option_a,
                    "B": q.option_b,
                    "C": q.option_c,
                },
            }
            for q in questions
        ]
    }


@router.post("/complete")
def complete_quiz(
    payload: dict,
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Persist quiz score into pointwallet and pointhistory
    """

    user_id = UUID(user["sub"])  # ✅ MOVED UP (FIX)
    today = date.today()

    # ✅ USER-SCOPED DAILY CHECK (FIX)
    already_completed = (
        db.query(PointHistory)
        .filter(
            PointHistory.user_id == user_id,     # ✅ per-user
            PointHistory.source == "Quiz",
            func.date(PointHistory.timestamp) == today,
        )
        .first()
    )

    if already_completed:
        raise HTTPException(
            status_code=400,
            detail="Daily quiz already completed",
        )

    score = payload.get("score")

    if score is None:
        raise HTTPException(status_code=400, detail="Score is required")

    if score < 0 or score > 30:
        raise HTTPException(status_code=400, detail="Invalid quiz score")

    # 1️⃣ Insert into pointhistory
    history = PointHistory(
        id=uuid4(),
        user_id=user_id,
        points=score,
        source="Quiz",
    )
    db.add(history)

    # 2️⃣ Update or create pointwallet
    wallet = (
        db.query(PointWallet)
        .filter(PointWallet.user_id == user_id)
        .first()
    )

    if wallet:
        wallet.total_points = (wallet.total_points or 0) + score
        wallet.updated_at = func.now()
    else:
        wallet = PointWallet(
            user_id=user_id,
            total_points=score,
            rank=None,  # handled later
        )
        db.add(wallet)

    db.commit()

    return {
        "message": "Quiz score persisted successfully",
        "points_added": score,
        "total_points": wallet.total_points,
    }


@router.get("/status")
def quiz_status(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(user["sub"])
    today = date.today()

    # ✅ USER-SCOPED STATUS CHECK (CORRECT)
    quiz_done_today = (
        db.query(PointHistory)
        .filter(
            PointHistory.user_id == user_id,
            PointHistory.source == "Quiz",
            func.date(PointHistory.timestamp) == today,
        )
        .first()
    )

    return {
        "completed": bool(quiz_done_today)
    }
