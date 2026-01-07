# app/routers/locations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from app.routers.deps import get_db
from app.models import schema

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("/", response_model=List[Dict[str, Optional[str]]])
def get_locations(db: Session = Depends(get_db)):
    """
    Return locations annotated with the plan_type from plans table.

    Response items:
    {
        "loc_id": "<uuid>",
        "loc_name": "Plant A",
        "plan_id": "<uuid or null>",
        "plan_type": "Prime" | "Nexus" | null
    }
    """
    # Use an outerjoin so locations without a linked plan still appear
    rows = (
        db.query(
            schema.Location.loc_id,
            schema.Location.loc_name,
            schema.Location.plan_id,
            schema.Plan.plan_type,  # assumes model name is `Plans` with attribute plan_type
        )
        .outerjoin(schema.Plan, schema.Location.plan_id == schema.Plan.plan_id)
        .order_by(schema.Location.loc_name)
        .all()
    )

    result = []
    for loc_id, loc_name, plan_id, plan_type in rows:
        result.append(
            {
                "loc_id": str(loc_id) if loc_id is not None else None,
                "loc_name": loc_name,
                "plan_id": str(plan_id) if plan_id is not None else None,
                "plan_type": plan_type,
            }
        )

    return result
