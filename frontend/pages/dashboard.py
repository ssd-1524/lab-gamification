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
st.markdown("## 👋 Welcome back")
st.markdown(f"### **{user['name']}**")

components.html(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;800&display=swap">
<style>
* {{
  font-family: 'Source Sans Pro' !important;
}}

.info-row {{
  display:flex;
  gap:24px;
  width:100%;
  margin-top:24px;
}}

.info-card {{
  flex:1;
  padding:22px;
  border-radius:18px;
  background:#ffffff;
  border:1px solid rgba(0,0,0,0.08);
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
  margin-top:4px;
}}
</style>

<div class="info-row">

  <div class="info-card bw">
    <div class="label">LOCATION</div>
    <div class="value">{user.get("loc_name","—")}</div>
  </div>

  <div class="info-card">
    <div class="label">ROLE</div>
    <div class="value">{user.get("role_name","—")}</div>
  </div>

</div>
""", height=120)

# ---------------- Metrics ---------------- #
components.html(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;800&display=swap">

<style>
* {{
  font-family: 'Source Sans Pro' !important;
}}

.metric-row {{
  display:flex;
  gap:24px;
  width:100%;
  margin:32px 0;
}}

.metric-card {{
  flex:1.6;
  padding:26px;
  border-radius:20px;
  background:#0b0b0b;
  color:white;
}}

.tier-card {{
  flex:1;
  background:white;
  color:black;
  border:1px solid rgba(0,0,0,.08);
}}

.label {{
  font-size:12px;
  font-weight:700;
  opacity:.7;
}}

.points {{
  font-size:44px;
  font-weight:800;
}}

.rank {{
  text-align:right;
}}

.tier {{
  font-size:24px;
  font-weight:800;
}}

.tier-body {{
  display:flex;
  align-items:center;
  gap:14px;
  margin-top:12px;
}}
</style>

<div class="metric-row">

  <div class="metric-card">
    <div style="display:flex;justify-content:space-between">
      <div>
        <div class="label">POINTS</div>
        <div class="points">{points}</div>
      </div>
      <div class="rank">
        <div class="label">RANK</div>
        <div class="points" style="font-size:40px">{rank}</div>
      </div>
    </div>

    <div style="margin-top:14px;font-size:14px;opacity:.85">
      Keep your streak — complete daily training to earn more points.
    </div>
  </div>

  <div class="metric-card tier-card">
    <div class="label">CURRENT TIER</div>
    <div class="tier">{tier}</div>
    <div class="tier-body">
      <img src="{badge}" height="52"/>
      <div style="font-size:14px;font-weight:600;color:#475569">Membership</div>
    </div>
  </div>

</div>
""", height=220)


# ---------------- Plant Growth ---------------- #
with st.container(border=True):
    st.markdown("## 🌱 Your Growth Journey")

    plant_state = get_plant_state()
    if plant_state:
        col_img, col_text = st.columns([2, 3])
        with col_img:
            st.image(plant_state["image_url"], width=280)
        with col_text:
            st.markdown(f"### {plant_state['message']}")
            st.markdown(f"#### 🔥 Login Streak: **{plant_state['streak']} days**")

            if plant_state.get("can_replant"):
                if st.button("🌱 Plant seed again"):
                    log_event("plant", "replanted")
                    st.success("A new seed has been planted 🌱 Come back tomorrow!")
                    st.rerun()

st.divider()

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
