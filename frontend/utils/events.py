from __future__ import annotations

import threading
from typing import Any, Dict, Optional

import requests
import streamlit as st

from utils.api_client import API_BASE_URL


def _post_event(
    access_token: str,
    payload: Dict[str, Any],
) -> None:
    """
    Background worker: sends the event to backend.
    This must NEVER touch session_state or Streamlit UI.
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        requests.post(
            f"{API_BASE_URL}/events",
            json=payload,
            headers=headers,
            timeout=3,
        )
    except Exception:
        # Analytics must never break UX
        pass


def log_event(
    feature: str,
    action: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Fire-and-forget event logger.

    Rules:
    - Never blocks UI
    - Never mutates session_state
    - Never forces rerun
    - Never raises
    """
    try:
        access_token = st.session_state.get("access_token")
        if not access_token:
            return

        payload: Dict[str, Any] = {
            "feature": feature,
            "action": action,
            "metadata": metadata or {},
        }

        worker = threading.Thread(
            target=_post_event,
            args=(access_token, payload),
            daemon=True,
        )
        worker.start()

    except Exception:
        # Never let analytics crash UX
        pass
