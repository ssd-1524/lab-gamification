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


@router.get("/stream")
def anomaly_stream(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Generate last 60 minutes of synthetic anomaly sensor data.
    Available only for Prime and Nexus plans.
    """

    user_id = user["user_id"]

    plan_name = (
        db.query(schema.Plans.plan_name)
        .join(schema.Users, schema.Users.plan_id == schema.Plans.plan_id)
        .filter(schema.Users.user_id == user_id)
        .scalar()
    )

    if plan_name not in ("Prime", "Nexus"):
        raise HTTPException(
            status_code=403,
            detail="Upgrade to Prime or Nexus to access Anomaly Detection",
        )

    now = datetime.now(IST)
    data = []

    base = random.randint(40, 55)

    for i in range(60):
        ts = now - timedelta(minutes=59 - i)

        drift = random.randint(-3, 4)
        spike = random.randint(20, 45) if random.random() < 0.07 else 0

        value = base + drift + spike

        data.append({
            "ts": ts.isoformat(),
            "value": value,
        })

    return data
