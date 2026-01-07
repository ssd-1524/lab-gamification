from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import pytz

from app.routers.deps import get_authenticated_user, get_db
from app.models import schema
from app.schemas.event import EventCreate

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/events", tags=["Events"])

IST = pytz.timezone("Asia/Kolkata")
@router.post("/")
def create_event(
    payload: EventCreate,
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    user_id = identity.get("user_id")
    if not user_id:
        raise HTTPException(401, "Unauthenticated")

    # ---------- Resolve active session ----------
    session_id = (
        db.query(schema.Sessions.session_id)
        .filter(
            schema.Sessions.user_id == user_id,
            schema.Sessions.logout_time.is_(None),
        )
        .order_by(schema.Sessions.login_time.desc())
        .scalar()
    )
    if not session_id:
        raise HTTPException(400, "No active session for user")

    # ---------- Resolve plan_id ----------
    loc_id = db.query(schema.Users.loc_id).filter(schema.Users.user_id == user_id).scalar()
    if not loc_id:
        raise HTTPException(400, "User has no location")

    plan_id = db.query(schema.Location.plan_id).filter(schema.Location.loc_id == loc_id).scalar()
    if not plan_id:
        raise HTTPException(400, "Location has no plan")

    # ---------- Insert Event ----------
    event = schema.Event(
        event_id=uuid4(),
        user_id=user_id,
        session_id=session_id,
        plan_id=plan_id,
        feature=payload.feature,
        action=payload.action,
        timestamp=datetime.now(IST),
        metadata=payload.metadata or {},
    )

    db.add(event)
    db.commit()

    return {"status": "ok"}