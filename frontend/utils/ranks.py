from __future__ import annotations

from typing import Dict, List, Tuple

import streamlit as st

from utils.events import record_event
from utils.popup import show_popup


# ------------------ Rank Thresholds ------------------ #

_RANK_THRESHOLDS: List[Tuple[str, int]] = [
    ("Bronze", 0),
    ("Silver", 200),
    ("Gold", 500),
    ("Platinum", 800),
]


def evaluate_rank(total_points: int) -> None:
    """Evaluate and update user rank based on total points."""
    current_rank = st.session_state.get("rank", "Bronze")
    new_rank = current_rank

    for rank, threshold in _RANK_THRESHOLDS:
        if total_points >= threshold:
            new_rank = rank

    if new_rank != current_rank:
        st.session_state["rank"] = new_rank

        record_event(
            feature="rank",
            action="promoted",
            metadata={"new_rank": new_rank},
        )

        st.session_state["popup_rank"] = True
        show_popup(
            title="Rank Up!",
            message=f"You are now ranked {new_rank} 🎖️",
            icon="🎖️",
            key="popup_rank",
        )
