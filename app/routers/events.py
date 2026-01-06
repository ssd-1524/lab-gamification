from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.routers.deps import get_db
from app.models.schema import Event
from app.routers.deps import get_authenticated_user
from app.schemas.event import EventCreate
import pytz
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Events"])

IST = pytz.timezone("Asia/Kolkata")
@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_authenticated_user),
):
    """
    Insert a single analytics / gamification event.

    Frontend provides only:
      - feature
      - action
      - metadata

    Backend injects:
      - user_id
      - session_id
      - plan_id
    """

    try:
        event = Event(
            user_id=user["user_id"],
            session_id=user["session_id"],
            plan_id=user["plan_id"],
            feature=payload.feature,
            action=payload.action,
            timestamp=datetime.now(IST),
            event_metadata=payload.metadata,
        )

        db.add(event)
        db.commit()
        return {"status": "ok"}

    except Exception as exc:
        db.rollback()
        print("EVENT INSERT FAILED:", exc)   # 🔴 ADD THIS
        raise

