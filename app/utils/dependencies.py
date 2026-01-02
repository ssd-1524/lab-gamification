from __future__ import annotations

from fastapi import Depends
from app.utils.auth import get_current_user


def get_authenticated_user(user: dict = Depends(get_current_user)) -> dict:
    """Dependency wrapper to inject authenticated Supabase user claims."""
    return user
