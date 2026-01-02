from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.events import record_event
from utils.popup import show_popup


# ------------------ Badge Rules ------------------ #

_BADGE_RULES: List[Dict[str, Any]] = [
    {"name": "Rising Star", "min_points": 100, "description": "Earn 100 points"},
    {"name": "Achiever", "min_points": 300, "description": "Earn 300 points"},
    {"name": "Champion", "min_points": 600, "description": "Earn 600 points"},
]


def evaluate_badges(total_points: int) -> None:
    """Evaluate and award badges based on total points."""
    if "badges" not in st.session_state:
        st.session_state["badges"] = []

    for rule in _BADGE_RULES:
        if total_points >= rule["min_points"] and rule["name"] not in st.session_state["badges"]:
            st.session_state["badges"].append(rule["name"])

            record_event(
                feature="badge",
                action="unlocked",
                metadata={"badge": rule["name"]},
            )

            st.session_state["popup_badge"] = True
            show_popup(
                title="New Badge Unlocked!",
                message=f"You earned the {rule['name']} badge 🏅",
                icon="🏅",
                key="popup_badge",
            )
