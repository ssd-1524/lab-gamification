from __future__ import annotations

import threading
from typing import Any, Dict, Optional
import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"


def _post_event(token: str, payload: Dict[str, Any]) -> None:
    """
    Background worker.
    Never touches Streamlit state.
    Never raises.
    """
    try:
        requests.post(
            f"{API_BASE_URL}/events/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
    except Exception:
        pass


def log_event(feature: str, action: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Fire-and-forget analytics logger.

    Guarantees:
    • never blocks UI
    • never mutates session_state
    • never forces rerun
    • never crashes UX
    """
    try:
        token = st.session_state.get("access_token")
        if not token:
            return

        payload = {
            "feature": feature,
            "action": action,
            "metadata": metadata or {},
        }

        threading.Thread(
            target=_post_event,
            args=(token, payload),
            daemon=True,
        ).start()

    except Exception:
        pass
