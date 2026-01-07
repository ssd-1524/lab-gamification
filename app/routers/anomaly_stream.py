from __future__ import annotations

import random
from datetime import datetime, timedelta
import pytz

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deps import get_authenticated_user, get_db
from app.models import schema

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/anomaly", tags=["Anomaly Stream"])

# Global anomaly memory (per-process)
LAST_ANOMALY_AT: dict[str, datetime] = {}


@router.get("/stream")
def anomaly_stream(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Generates 60-minute sliding sensor window.
    Creates anomaly only once every 30 seconds.
    """

    user_id = user["user_id"]

    plan = (
        db.query(schema.Plan.plan_type)
        .join(schema.Location, schema.Location.plan_id == schema.Plan.plan_id)
        .join(schema.Users, schema.Users.loc_id == schema.Location.loc_id)
        .filter(schema.Users.user_id == user_id)
        .scalar()
    )

    if plan not in ("Prime", "Nexus"):
        raise HTTPException(403, "Upgrade to Prime or Nexus to access Anomaly Detection")

    now = datetime.now(IST)
    base = random.randint(45, 55)

    last = LAST_ANOMALY_AT.get(user_id)
    allow_spike = not last or (now - last) > timedelta(seconds=30)

    data = []

    for i in range(60):
        ts = now - timedelta(minutes=59 - i)

        drift = random.randint(-3, 3)

        spike = 0
        if i == 59 and allow_spike and random.random() < 0.5:
            spike = random.randint(35, 60)
            LAST_ANOMALY_AT[user_id] = now

        value = base + drift + spike

        data.append({
            "ts": ts.isoformat(),
            "value": value,
        })

    return data
