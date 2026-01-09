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

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("📍 **Location**")
        st.markdown(user.get("loc_name", "—"))
    with col2:
        st.markdown("🛠️ **Role**")
        st.markdown(user.get("role_name", "—"))

st.divider()

# ---------------- Metrics ---------------- #
components.html(f"""
<style>
.metric-row {{
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 28px;
  width: 100%;
  margin: 36px 0;
  font-family: 'Source Sans Pro', Arial, sans-serif;
}}

.metric-card {{
  padding: 28px;
  border-radius: 22px;
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.08);
}}

.bw-card {{
  background: #0b0b0b;
  color: #ffffff;
}}

.label {{
  font-size: 12px;
  font-weight: 700;
  opacity: 0.65;
  letter-spacing: 0.04em;
}}

.points {{
  font-size: 48px;
  font-weight: 800;
  margin-top: 2px;
}}

.rank {{
  text-align: right;
}}

.subtext {{
  margin-top: 14px;
  font-size: 14px;
  opacity: 0.85;
}}

.tier {{
  font-size: 26px;
  font-weight: 800;
  margin-top: 6px;
}}

.tier-body {{
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
}}
</style>

<div class="metric-row">

  <div class="metric-card bw-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <div class="label">POINTS</div>
        <div class="points">{points}</div>
      </div>
      <div class="rank">
        <div class="label">RANK</div>
        <div class="points" style="font-size:30px">{rank}</div>
      </div>
    </div>

    <div class="subtext">
      Keep your streak — complete daily training to earn more points.
    </div>
  </div>

  <div class="metric-card">
    <div class="label">CURRENT TIER</div>
    <div class="tier">{tier}</div>

    <div class="tier-body">
      <img src="{badge}" height="54"/>
      
    </div>
  </div>

</div>
""", height=240)


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
