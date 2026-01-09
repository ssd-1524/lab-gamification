from __future__ import annotations

import streamlit as st
import requests
import pandas as pd

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

data = resp.json()

if not data:
    st.info("No leaderboard data available.")
    st.stop()

rows = []
me_index = None

for i, row in enumerate(data):
    rows.append(
        {
            "Badge": row["badge_image"] or "—",
            "Name": row["name"],
            "Points": f'{row["points"]} pts',
            "Rank": row["rank"] or "—",
        }
    )
    if row["is_me"]:
        me_index = i

df = pd.DataFrame(rows)

# ---------- Highlight current user ----------
def highlight_me(row):
    if row.name == me_index:
        return ["background-color: rgba(0,0,0,0.06); font-weight:700"] * len(row)
    return [""] * len(row)

# ---------- Style outer card ----------
st.markdown(
    """
<style>
div[data-testid="stDataFrame"] {
    border: 5px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    padding: 14px;
    background: #ffffff;
}
</style>
""",
    unsafe_allow_html=True,
)

st.dataframe(
    df.style.apply(highlight_me, axis=1),
    use_container_width=True,
    hide_index=True,
)
