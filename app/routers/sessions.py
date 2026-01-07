from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from sqlalchemy import text
from app.routers.deps import get_db
from app.routers.deps import get_authenticated_user
from app.models import schema
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a login session entry for the authenticated user."""
    _ = user
    _ = db
    return {"status": "session_created"}


@router.get("/streak")
def get_login_streak(
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    uid = identity["user_id"]

    row = db.execute(
        text("SELECT streak FROM login_streak_view WHERE user_id = :uid"),
        {"uid": uid},
    ).fetchone()

    return {"streak": int(row.streak) if row else 0}

@router.post("/logout")
def logout(user: dict = Depends(get_authenticated_user), db: Session = Depends(get_db)):
    session = (
        db.query(schema.Sessions)
        .filter(schema.Sessions.user_id == user["user_id"])
        .order_by(schema.Sessions.login_time.desc())
        .first()
    )

    if session:
        session.logout_time = datetime.now(IST)
        db.commit()

    return {"status": "logged_out"}