from __future__ import annotations

import random
from datetime import datetime, timedelta
import pytz

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deps import get_authenticated_user, get_db
from app.models import schema

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/optimizer", tags=["Optimizer Stream"])


@router.get("/stream")
def optimizer_stream(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Hourly optimization KPIs – Nexus only
    """
    user_id = user["user_id"]

    plan = (
        db.query(schema.Plans.plan_name)
        .join(schema.Users, schema.Users.plan_id == schema.Plans.plan_id)
        .filter(schema.Users.user_id == user_id)
        .scalar()
    )

    if plan != "Nexus":
        raise HTTPException(403, "Optimizer available only for Nexus plan")

    now = datetime.now(IST)
    data = []

    for i in range(24):
        ts = now - timedelta(hours=23 - i)

        data.append({
            "ts": ts.isoformat(),
            "efficiency": random.randint(65, 95),
            "cost": random.randint(750, 1300),
            "throughput": random.randint(18, 38),
        })

    return data
