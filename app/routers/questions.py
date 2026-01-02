from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import random

from app.routers.deps import get_db
from app.models.schema import Question

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/")
def get_questions_by_type(
    question_type: str = Query(...),
    db: Session = Depends(get_db),
):
    questions = (
        db.query(Question)
        .filter(Question.question_type == question_type)
        .all()
    )

    if not questions:
        return []

    return questions
