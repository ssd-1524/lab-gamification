from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deps import get_authenticated_user, get_db
from app.models import schema
from app.services.stream_workers import OPTIMIZER_BUFFER

router = APIRouter(prefix="/optimizer", tags=["Optimizer Stream"])


@router.get("/stream")
def optimizer_stream(
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Return live optimizer KPI feed.
    Available only for Nexus subscription.
    """

    user_id = identity["user_id"]

    plan_name = (
        db.query(schema.Plan.plan_type)
        .join(schema.Location, schema.Location.plan_id == schema.Plan.plan_id)
        .join(schema.Users, schema.Users.loc_id == schema.Location.loc_id)
        .filter(schema.Users.user_id == user_id)
        .scalar()
    )

    if plan_name != "Nexus":
        raise HTTPException(
            status_code=403,
            detail="Upgrade to Nexus to access Optimizer",
        )

    return OPTIMIZER_BUFFER
