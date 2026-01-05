from __future__ import annotations

from typing import List, Dict

import streamlit as st

from utils.api_client import get_leaderboard
from utils.sessions import is_authenticated
from utils.events import log_event


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")


# 🔴 PAGE VIEW EVENT
log_event("leaderboard", "page_view")


# ------------------ Data ------------------ #

leaderboard: List[Dict] = get_leaderboard(limit=10)


# ------------------ UI ------------------ #

st.title("🏆 Leaderboard")

if not leaderboard:
    st.info("No leaderboard data available yet.")
else:
    for idx, user in enumerate(leaderboard, start=1):
        cols = st.columns([1, 4, 2])
        with cols[0]:
            st.write(f"#{idx}")
        with cols[1]:
            if st.button(user["name"], key=f"user_{user['user_id']}"):
                log_event(
                    "leaderboard",
                    "user_inspect",
                    {"target_user_id": user["user_id"]},
                )
        with cols[2]:
            st.write(f"{user['points']} pts")
