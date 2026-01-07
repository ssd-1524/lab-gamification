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

# 🔒 Global in-memory anomaly state
ACTIVE_ANOMALY_UNTIL: datetime | None = None


@router.get("/stream")
def anomaly_stream(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    global ACTIVE_ANOMALY_UNTIL

    user_id = user["user_id"]

    plan_name = (
        db.query(schema.Plan.plan_type)
        .join(schema.Location, schema.Location.plan_id == schema.Plan.plan_id)
        .join(schema.Users, schema.Users.loc_id == schema.Location.loc_id)
        .filter(schema.Users.user_id == user_id)
        .scalar()
    )

    if plan_name not in ("Prime", "Nexus"):
        raise HTTPException(403, "Upgrade to Prime or Nexus to access Anomaly Detection")

    now = datetime.now(IST)

    # Start anomaly once every ~5 minutes
    if ACTIVE_ANOMALY_UNTIL is None and random.random() < 0.10:
        ACTIVE_ANOMALY_UNTIL = now + timedelta(minutes=2)

    # Clear expired anomaly
    if ACTIVE_ANOMALY_UNTIL and now > ACTIVE_ANOMALY_UNTIL:
        ACTIVE_ANOMALY_UNTIL = None

    data = []
    base = random.randint(40, 55)

    for i in range(60):
        ts = now - timedelta(minutes=59 - i)
        drift = random.randint(-3, 4)

        # Anomaly only while ACTIVE
        if i == 59 and ACTIVE_ANOMALY_UNTIL:
            spike = random.randint(25, 45)
        else:
            spike = 0

        value = base + drift + spike

        data.append({"ts": ts.isoformat(), "value": value})

    return data
