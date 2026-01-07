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
    """
    Returns 24 hourly optimization KPI points.
    If the latest hour looks improvable (low efficiency) and the user hasn't
    been suggested recently, the latest point will include a `suggestion` object.

    Access: Nexus only (enforced here).
    """

    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    # ---------- Resolve plan robustly ----------
    try:
        # 1) Try to fetch loc_id from users table first (safe and simple)
        loc_id = db.query(schema.Users.loc_id).filter(schema.Users.user_id == user_id).scalar()
    except Exception as e:
        # Defensive: log and deny access (avoid crashing the endpoint)
        print("optimizer_stream: error querying Users.loc_id:", e)
        raise HTTPException(status_code=500, detail="Server error resolving user location")

    if not loc_id:
        # no location -> deny
        raise HTTPException(status_code=403, detail="User location not found; upgrade or contact admin")

    try:
        # 2) Fetch plan row via Location -> Plans relationship
        plan_row = (
            db.query(schema.Plans)
            .join(schema.Location, schema.Location.plan_id == schema.Plans.plan_id)
            .filter(schema.Location.loc_id == loc_id)
            .first()
        )
    except Exception as e:
        # Defensive: fallback attempt using an alternate join order (if model names differ)
        print("optimizer_stream: primary plan lookup failed, attempting fallback. error:", e)
        plan_row = None

    if not plan_row:
        # fallback: try get plan_id directly from location, then fetch plan
        try:
            plan_id = db.query(schema.Location.plan_id).filter(schema.Location.loc_id == loc_id).scalar()
            if plan_id:
                plan_row = db.query(schema.Plans).filter(schema.Plans.plan_id == plan_id).first()
        except Exception as e:
            print("optimizer_stream: fallback plan lookup failed:", e)
            plan_row = None

    # determine plan name (support both 'plan_name' and 'plan_type' columns)
    plan_name: Optional[str] = None
    if plan_row is not None:
        plan_name = getattr(plan_row, "plan_name", None) or getattr(plan_row, "plan_type", None)

    if not plan_name:
        # If we cannot determine plan, deny access for safety
        raise HTTPException(status_code=403, detail="Could not determine plan for user")

    # normalize string comparison
    plan_name_norm = str(plan_name).strip().lower()

    # Check access: optimizer available only for Nexus plan
    if plan_name_norm != "nexus":
        raise HTTPException(status_code=403, detail="Optimizer available only for Nexus plan")

    # ---------- Build synthetic hourly KPI stream ----------
    now = datetime.now(IST)
    data: List[Dict[str, Any]] = []

    # Rate-limit suggestions to once per hour per user (in-memory)
    last_suggested: Optional[datetime] = _LAST_OPTIMIZE_AT.get(str(user_id))
    allow_suggestion = not last_suggested or (now - last_suggested) >= timedelta(hours=1)

    for i in range(24):
        ts = now - timedelta(hours=23 - i)

        # Efficiency: lower is worse (60-95)
        efficiency = random.randint(60, 95)
        cost = random.randint(700, 1400)
        throughput = random.randint(10, 45)

        point: Dict[str, Any] = {
            "ts": ts.isoformat(),
            "efficiency": efficiency,
            "cost": cost,
            "throughput": throughput,
            # include suggestion key always for predictability on frontend
            "suggestion": {"suggested": False},
        }

        # Decide suggestion only on the latest point
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

            # record suggestion time
            _LAST_OPTIMIZE_AT[str(user_id)] = now

        data.append(point)

    return data
