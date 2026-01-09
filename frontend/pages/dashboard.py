from __future__ import annotations
import streamlit as st
import time
import requests
from datetime import datetime
from pytz import timezone
import streamlit.components.v1 as components

from utils.api_client import get_user_points, get_plant_state
from utils.events import log_event
from utils.sessions import get_access_token
from utils.ui_utils import FEATURE_GUIDES
from utils.theme import apply_theme

API_BASE_URL = "https://lab-gamification.onrender.com"
IST = timezone("Asia/Kolkata")

st.set_page_config(page_title="Dashboard - Stomata Labs", page_icon="📊", layout="wide")
apply_theme()

# ---------------- Security ---------------- #
if not st.session_state.get("is_authenticated"):
    st.warning("Please login to access the dashboard.")
    st.switch_page("streamlit_app.py")
    st.stop()

log_event("dashboard", "page_view")

user = st.session_state.user
token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Data ---------------- #
rank_resp = requests.get(f"{API_BASE_URL}/users/me/rank", headers=headers)
rank_data = rank_resp.json() if rank_resp.status_code == 200 else {}

points = rank_data.get("points", 0)
rank = rank_data.get("position", "—")
tier = rank_data.get("rank", "—")
badge = rank_data.get("badge_image") or ""

# ---------------- Header ---------------- #
st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;800&display=swap">
<div style="
    margin-top:6px;
    margin-bottom:22px;
    font-family:'Source Sans Pro' !important;
">
  <div style="font-size:13px; font-weight:600; color:#64748b; letter-spacing:.04em;">
    WELCOME BACK
  </div>
  <div style="font-size:34px; font-weight:800; color:#0f172a; margin-top:4px;">
    {user['name']}
  </div>
</div>
""", unsafe_allow_html=True)


components.html(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;800&display=swap">
<style>
.row {{
  display:flex;
  gap:24px;
  width:100%;
  margin:28px 0;
}}

.card {{
  flex:1;
  padding:24px;
  border-radius:20px;
  border:5px solid rgba(0,0,0,0.08);
  background:#ffffff;
  font-family:'Source Sans Pro';
}}

.bw {{
  background:#0b0b0b;
  color:white;
}}

.label {{
  font-size:12px;
  font-weight:700;
  opacity:.65;
  letter-spacing:.04em;
}}

.value {{
  font-size:18px;
  font-weight:700;
  margin-top:6px;
}}

.points {{
  font-size:42px;
  font-weight:800;
}}

.rank {{
  font-size:42px;
  font-weight:800;
  text-align:right;
}}
</style>

<div class="row">
  <div class="card ">
    <div class="label">LOCATION</div>
    <div class="value">{user.get("loc_name","—")}</div>
  </div>

  <div class="card bw">
    <div class="label">ROLE</div>
    <div class="value">{user.get("role_name","—")}</div>
  </div>
</div>

<div class="row">
  <div class="card bw">
    <div style="display:flex;justify-content:space-between">
      <div>
        <div class="label">POINTS</div>
        <div class="points">{points}</div>
      </div>
      <div style="text-align:right">
        <div class="label">RANK</div>
        <div class="rank">{rank}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="label">CURRENT TIER</div>
    <div class="value" style="font-size:22px;font-weight:800">{tier}</div>
    <div style="display:flex;align-items:center;gap:14px;margin-top:14px">
      <img src="{badge}" height="52"/>
    </div>
  </div>
</div>
""", height=380)


# ---------------- Plant Growth ---------------- #
components.html("""
<div class="card">
  <div style="font-size:13px;font-weight:700;color:#64748b;letter-spacing:.04em;margin-bottom:12px;">
    YOUR GROWTH JOURNEY
  </div>
</div>
""", height=0)

plant_state = get_plant_state()

if plant_state:
    col_img, col_text = st.columns([1.4, 3])

    with col_img:
        st.image(plant_state["image_url"], width=240)

    with col_text:
        st.markdown(f"""
        <div style="font-size:20px;font-weight:700;color:#0f172a;">
            {plant_state['message']}
        </div>
        <div style="margin-top:6px;font-size:14px;font-weight:600;color:#475569;">
            🔥 Login Streak:
            <span style="font-weight:800;color:#0f172a;">{plant_state['streak']} days</span>
        </div>
        """, unsafe_allow_html=True)

        if plant_state.get("can_replant"):
            if st.button("🌱 Plant seed again"):
                log_event("plant", "replanted")
                st.success("A new seed has been planted 🌱 Come back tomorrow!")
                st.rerun()

# ---------------- Guides ---------------- #
st.subheader("📖 Feature Guides")
cols = st.columns(len(FEATURE_GUIDES))

for i, (key, data) in enumerate(FEATURE_GUIDES.items()):
    with cols[i]:
        if st.button(f"{data['title']}\n{data['subtitle']}", use_container_width=True):
            log_event("guides", "open_from_dashboard", {"guide": key})
            st.session_state.selected_guide = key
            st.switch_page("pages/guides.py")

st.divider()

# ---------------- Quiz ---------------- #
quiz_resp = requests.get(f"{API_BASE_URL}/quizzes/status", headers=headers)
quiz_completed = quiz_resp.json().get("completed", False) if quiz_resp.status_code == 200 else False

if not quiz_completed:
    with st.container(border=True):
        st.markdown("### 🎯 Daily Training Available")
        st.caption("Complete today’s quiz to maintain your streak and earn bonus points.")
        if st.button("🚀 Start Quiz", use_container_width=True):
            log_event("dashboard", "start_quiz_click")
            st.switch_page("pages/quizzes.py")
