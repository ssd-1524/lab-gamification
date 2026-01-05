from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schema import Badge, UserBadge
from app.routers.deps import get_db
from app.routers.deps import get_authenticated_user

router = APIRouter(prefix="/badges", tags=["Badges"])


@router.get("", response_model=List[dict])
def get_user_badges(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Return badges earned by the authenticated user."""
    user_id = user["sub"]

    rows = (
        db.query(Badge)
        .join(UserBadge, Badge.badge_id == UserBadge.badge_id)
        .filter(UserBadge.user_id == user_id)
        .all()
    )

    return [{"name": badge.name, "description": badge.description} for badge in rows]
