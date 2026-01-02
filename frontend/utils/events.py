from __future__ import annotations

from typing import Any, Dict

from utils.api_client import log_event
from utils.sessions import get_access_token


def record_event(feature: str, action: str, metadata: Dict[str, Any]) -> bool:
    """Record a gamification event for the current user."""
    token = get_access_token()
    if not token:
        return False

    payload = {
        "feature": feature,
        "action": action,
        "metadata": metadata,
    }

    return log_event(token=token, payload=payload)
