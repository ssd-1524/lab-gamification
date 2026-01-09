from __future__ import annotations

import streamlit as st
import requests

from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event
from utils.theme import apply_theme

API_BASE_URL = "https://lab-gamification.onrender.com"

st.set_page_config(page_title="Leaderboard - Stomata Labs", layout="wide")
apply_theme()

# ---------------- Security ---------------- #
if not is_authenticated():
    st.switch_page("pages/auth.py")

log_event("leaderboard", "page_view")

headers = {"Authorization": f"Bearer {get_access_token()}"}
resp = requests.get(f"{API_BASE_URL}/users/leaderboard", headers=headers)

# ---------------- Styles ---------------- #
st.markdown("""
<style>
.leaderboard-card {
    border: 5px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    overflow: hidden;
    background: #ffffff;
}

.lb-table {
    width: 100%;
    border-collapse: collapse;
}

.lb-table th {
    text-align: left;
    font-size: 13px;
    font-weight: 700;
    padding: 14px 18px;
    background: #f8fafc;
    color: #475569;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

.lb-table td {
    padding: 14px 18px;
    font-size: 14px;
    color: #0f172a;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.lb-me {
    background: rgba(0,0,0,0.04);
    font-weight: 700;
}

.lb-badge img {
    vertical-align: middle;
}
</style>

<div class="leaderboard-card">
<table class="lb-table">
<thead>
<tr>
  <th>Badge</th>
  <th>Name</th>
  <th>Points</th>
  <th>Rank</th>
</tr>
</thead>
<tbody>
""", unsafe_allow_html=True)

# ---------------- Table Rows ---------------- #
for row in resp.json():
    row_class = "lb-me" if row["is_me"] else ""

    st.markdown(
        f"""
        <tr class="{row_class}">
            <td class="lb-badge">
                {f"<img src='{row['badge_image']}' width='34'>" if row["badge_image"] else "—"}
            </td>
            <td>{row['name']}</td>
            <td>{row['points']} pts</td>
            <td>{row['rank'] or "—"}</td>
        </tr>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Close Table ---------------- #
st.markdown("""
</tbody>
</table>
</div>
""", unsafe_allow_html=True)
