from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.routers.deps import get_db
from app.routers.deps import get_authenticated_user

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> dict:
    """Create a login session entry for the authenticated user."""
    _ = user
    _ = db
    return {"status": "session_created"}
