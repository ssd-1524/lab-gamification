from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schema import Location, Question, Users
from app.routers.deps import get_db
from app.utils.dependencies import get_authenticated_user

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("/today")
def get_today_quiz(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> Dict[str, List[dict]]:
    """Return today's quiz questions for the authenticated user."""
    user_id = user["sub"]

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
