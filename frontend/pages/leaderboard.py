from __future__ import annotations

import streamlit as st
import requests

from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event
from utils.theme import apply_theme

API_BASE_URL = "https://lab-gamification.onrender.com"

st.set_page_config(page_title="Leaderboard - Stomata Labs", page_icon="🏆", layout="wide")
apply_theme()

if not is_authenticated():
    st.switch_page("pages/auth.py")

log_event("leaderboard", "page_view")

headers = {"Authorization": f"Bearer {get_access_token()}"}
resp = requests.get(f"{API_BASE_URL}/users/leaderboard", headers=headers)

st.subheader("🏆 Leaderboard")

if resp.status_code != 200:
    st.error("Failed to load leaderboard.")
    st.stop()

rows = resp.json()

# ---------- Card Wrapper ----------
st.markdown("""
<style>
.lb-wrapper {
    border-radius: 18px;
    padding: 18px 10px;
    background: #ffffff;
}

.lb-head, .lb-row {
    display: grid;
    grid-template-columns: 70px 1fr 140px 120px;
    padding: 10px 18px;
    align-items: center;
}

.lb-head {
    font-weight: 700;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

.lb-row:not(:last-child) {
    border-bottom: 1px solid rgba(0,0,0,0.05);
}

.lb-me {
    background: #0b0b0b;
    color: #ffffff;
    font-weight: 800;
}

.lb-me div {
    color: #ffffff !important;
}

</style>

<div class="lb-wrapper">
  <div class="lb-head">
    <div>Badge</div><div>Name</div><div>Points</div><div>Rank</div>
  </div>
""", unsafe_allow_html=True)

# ---------- Rows ----------
for row in rows:
    cls = "lb-row lb-me" if row["is_me"] else "lb-row"
    badge = row["badge_image"]
    badge_html = f"<img src='{badge}' width='36'>" if badge else "—"

    st.markdown(
        f"""
        <div class="{cls}">
            <div>{badge_html}</div>
            <div>{row["name"]}</div>
            <div>{row["points"]} pts</div>
            <div>{row["rank"] or "—"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
