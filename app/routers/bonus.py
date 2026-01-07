from __future__ import annotations

from uuid import uuid4
from datetime import datetime
import pytz

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deps import get_authenticated_user, get_db
from app.schemas.bonus import BonusRequest
from app.models.schema import PointWallet, PointHistory, Event, Users, Location

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/bonus", tags=["Bonus"])


@router.post("/reward")
def reward_bonus(
    payload: BonusRequest,
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    user_id = identity["user_id"]
    session_id = identity["session_id"]

    if payload.points <= 0:
        raise HTTPException(status_code=400, detail="Points must be positive")

    # Resolve plan_id
    plan_id = (
        db.query(Location.plan_id)
        .join(Users, Users.loc_id == Location.loc_id)
        .filter(Users.user_id == user_id)
        .scalar()
    )


    # Update wallet
    wallet = db.query(PointWallet).filter(PointWallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.total_points += payload.points

    # Insert history
    db.add(PointHistory(
        id=uuid4(),
        user_id=user_id,
        points=payload.points,
        source="Bonus",
    ))

    # Insert event
    db.add(Event(
        event_id=uuid4(),
        user_id=user_id,
        session_id=session_id,
        plan_id=plan_id,
        feature=payload.feature,
        action="accepted",
        event_metadata=payload.metadata,
        timestamp=datetime.now(IST),
    ))

    db.commit()

    return {
        "message": "Bonus rewarded",
        "points_added": payload.points,
        "total_points": wallet.total_points,
    }
