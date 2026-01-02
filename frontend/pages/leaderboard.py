from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.session import is_authenticated


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")


# ------------------ Page Header ------------------ #

st.title("🏆 Leaderboard")


# ------------------ Fetch Leaderboard (Placeholder) ------------------ #

def _fetch_leaderboard() -> List[Dict[str, Any]]:
    return [
        {"name": "Alice", "points": 420, "rank": "Gold"},
        {"name": "Bob", "points": 360, "rank": "Silver"},
        {"name": "Charlie", "points": 300, "rank": "Bronze"},
    ]


leaderboard = _fetch_leaderboard()

st.markdown("### 🌟 Top Performers")

for idx, user in enumerate(leaderboard, start=1):
    st.write(f"{idx}. **{user['name']}** — {user['points']} pts ({user['rank']})")
