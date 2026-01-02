from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.sessions import get_current_user, is_authenticated


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")


# ------------------ Fetch Profile Data (Placeholder) ------------------ #

def _fetch_profile() -> Dict[str, Any]:
    return {
        "total_points": 420,
        "rank": "Gold",
        "badges": ["Rising Star", "Achiever"],
        "history": [
            {"event": "Login Quiz", "points": 50},
            {"event": "Daily Quiz", "points": 30},
        ],
    }


profile: Dict[str, Any] = _fetch_profile()
user = get_current_user()

st.title("👤 My Profile")
st.write(f"**Name:** {user.get('name', 'User')}")

st.markdown("### 🪙 Points Wallet")
st.metric("Total Points", profile["total_points"])
st.metric("Rank", profile["rank"])

st.markdown("### 🏅 Badges Earned")
for badge in profile["badges"]:
    st.write(f"• {badge}")

st.markdown("### 📜 Points History")
for item in profile["history"]:
    st.write(f"{item['event']} — {item['points']} pts")
