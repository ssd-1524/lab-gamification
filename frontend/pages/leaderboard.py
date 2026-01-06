import streamlit as st
import requests
from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event

API_BASE_URL = "http://localhost:8000"

if not is_authenticated():
    st.switch_page("pages/auth.py")

log_event("leaderboard", "page_view")

headers = {"Authorization": f"Bearer {get_access_token()}"}
resp = requests.get(f"{API_BASE_URL}/users/leaderboard", headers=headers)

st.markdown("""
<style>
.lb-table {
    border-radius: 16px;
    overflow: hidden;
    background: var(--secondary-background-color);
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
}
.lb-row {
    display: grid;
    grid-template-columns: 60px 1fr 120px 120px;
    padding: 12px 16px;
    align-items: center;
}
.lb-row:not(:last-child) {
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.lb-me {
    background: linear-gradient(90deg, rgba(255,75,75,0.15), transparent);
}
.lb-head {
    font-weight: 700;
    opacity: 0.85;
}
</style>
<div class="lb-table">
  <div class="lb-row lb-head">
    <div>🏅</div><div>Name</div><div>Points</div><div>Rank</div>
  </div>
""", unsafe_allow_html=True)

for row in resp.json():
    me_class = "lb-row lb-me" if row["is_me"] else "lb-row"

    st.markdown(
        f"""
        <div class="{me_class}">
            <div>{f"<img src='{row['badge_image']}' width='34'>" if row["badge_image"] else "—"}</div>
            <div>{row['name']}</div>
            <div>{row['points']} pts</div>
            <div>{row['rank'] or "—"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)
