from __future__ import annotations

import random
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.routers.deps import get_authenticated_user, get_db
from app.models import schema

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/optimizer", tags=["Optimizer Stream"])

# In-memory rate-limit for suggestions per-user (survives process lifetime only)
_LAST_OPTIMIZE_AT: Dict[str, datetime] = {}


@router.get("/stream")
def optimizer_stream(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:

    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    # ---------- Resolve plan_id safely ----------
    loc_id = db.query(schema.Users.loc_id).filter(schema.Users.user_id == user_id).scalar()
    if not loc_id:
        raise HTTPException(status_code=403, detail="User has no location assigned")

    plan_id = db.query(schema.Location.plan_id).filter(schema.Location.loc_id == loc_id).scalar()
    if not plan_id:
        raise HTTPException(status_code=403, detail="Location has no plan assigned")

    # ---------- Resolve plan_type explicitly ----------
    plan_type = db.query(schema.Plan.plan_type).filter(schema.Plan.plan_id == plan_id).scalar()
    if not plan_type:
        raise HTTPException(status_code=403, detail="Plan type not found for user")

    plan_type_norm = str(plan_type).strip().lower()

    # 🔥 FINAL AUTHORITY CHECK
    if plan_type_norm != "nexus":
        raise HTTPException(status_code=403, detail="Optimizer available only for Nexus plan")

    # ---------- Build synthetic hourly KPI stream ----------
    now = datetime.now(IST)
    data: List[Dict[str, Any]] = []

    last_suggested: Optional[datetime] = _LAST_OPTIMIZE_AT.get(str(user_id))
    allow_suggestion = not last_suggested or (now - last_suggested) >= timedelta(hours=1)

    for i in range(24):
        ts = now - timedelta(hours=23 - i)

        efficiency = random.randint(60, 95)
        cost = random.randint(700, 1400)
        throughput = random.randint(10, 45)

        point: Dict[str, Any] = {
            "ts": ts.isoformat(),
            "efficiency": efficiency,
            "cost": cost,
            "throughput": throughput,
            "suggestion": {"suggested": False},
        }

        if i == 23 and allow_suggestion and efficiency < 75 and random.random() < 0.45:
            impact_pct = random.randint(5, 20)
            severity = "High" if efficiency < 65 else "Medium"
            suggested_points = 20 if severity == "High" else 10

            point["suggestion"] = {
                "suggested": True,
                "severity": severity,
                "estimated_efficiency_gain_pct": impact_pct,
                "suggested_points": suggested_points,
                "reason": "Lower than expected efficiency",
                "suggested_at": now.isoformat(),
            }

            _LAST_OPTIMIZE_AT[str(user_id)] = now

        data.append(point)

    return data
