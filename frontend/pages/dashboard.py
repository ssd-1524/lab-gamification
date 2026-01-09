from __future__ import annotations
import streamlit as st
import time
import requests
from datetime import datetime
from pytz import timezone
from textwrap import dedent

from utils.api_client import get_user_points
from utils.events import log_event
from utils.sessions import get_access_token
from utils.api_client import get_plant_state
from utils.ui_utils import FEATURE_GUIDES
from utils.theme import apply_theme


API_BASE_URL = "https://lab-gamification.onrender.com"

st.set_page_config(page_title="Dashboard - Stomata Labs", page_icon="📊", layout="wide")
IST = timezone("Asia/Kolkata")
apply_theme()

# ---------------- Security ---------------- #
if not st.session_state.get("is_authenticated"):
    st.warning("Please login to access the dashboard.")
    st.switch_page("streamlit_app.py")
    st.stop()

log_event("dashboard", "page_view")

user = st.session_state.user
points_data = get_user_points()

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Quiz Status ---------------- #
quiz_resp = requests.get(f"{API_BASE_URL}/quizzes/status", headers=headers)
quiz_completed = quiz_resp.json().get("completed", False) if quiz_resp.status_code == 200 else False

# ---------------- Streak ---------------- #
streak_resp = requests.get(f"{API_BASE_URL}/sessions/streak", headers=headers)
streak = streak_resp.json().get("streak", 0) if streak_resp.status_code == 200 else 0

# ---------------- Rank ---------------- #
rank_resp = requests.get(f"{API_BASE_URL}/users/me/rank", headers=headers)
rank_data = rank_resp.json() if rank_resp.status_code == 200 else {}

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


st.markdown("""
<style>
.card-row {
    display:flex;
    gap:20px;
    align-items:stretch;
    width:100%;
}

.metric-card {
    flex:1;
    border-radius:16px;
    padding:22px;
    border:1px solid rgba(0,0,0,0.06);
    background:#ffffff;
}

.bw-card {
    background:#0a0a0a;
    color:white;
}

.bw-card .label {
    font-size:13px;
    font-weight:700;
    color:rgba(255,255,255,0.7);
}

.bw-card .points {
    font-size:42px;
    font-weight:800;
    margin-top:4px;
}

.bw-card .rank {
    text-align:right;
}

.bw-card .wallet-btn {
    margin-top:18px;
    padding:8px 16px;
    border:1px solid rgba(255,255,255,0.25);
    border-radius:10px;
    display:inline-block;
    font-weight:700;
}

.tier-card .title {
    font-size:13px;
    font-weight:700;
    color:#64748b;
}

.tier-card .tier {
    font-size:22px;
    font-weight:800;
    margin-top:4px;
}

.tier-body {
    display:flex;
    align-items:center;
    gap:14px;
    margin-top:14px;
}

.tier-body img {
    height:56px;
}
</style>
""", unsafe_allow_html=True)

points = rank_data.get("points", 0)
position = rank_data.get("position", "—")
tier = rank_data.get("rank", "—")
badge = rank_data.get("badge_image")

row_html = f"""
<div class="card-row">
    <div class="metric-card bw-card">
        <div style="display:flex;justify-content:space-between;">
            <div>
                <div class="label">POINTS</div>
                <div class="points">{points:,}</div>
            </div>
            <div class="rank">
                <div class="label">RANK</div>
                <div class="points" style="font-size:24px;">{position}</div>
            </div>
        </div>

        <div style="margin-top:12px;font-size:14px;color:rgba(255,255,255,0.85);">
            Keep your streak — complete daily training to earn more points.
        </div>

        <div class="wallet-btn">View Wallet</div>
    </div>

    <div class="metric-card tier-card">
        <div class="title">CURRENT TIER</div>
        <div class="tier">{tier}</div>
        <div class="tier-body">
            {f"<img src='{badge}' />" if badge else ""}
            <div style="font-size:13px;color:#475569;font-weight:600;">Membership</div>
        </div>
    </div>
</div>
"""

st.markdown(row_html, unsafe_allow_html=True)
st.divider()


# ---------------- Plant Growth Gamification ---------------- #
with st.container(border=True):
    st.markdown("## 🌱 Your Growth Journey")

    plant_state = get_plant_state()

    if plant_state:
        col_img, col_text = st.columns([2, 3], vertical_alignment="center")

        # -------- Plant Image --------
        with col_img:
            st.image(
                plant_state["image_url"],
                width=280,
            )

        # -------- Text Content --------
        with col_text:
            st.markdown(f"### {plant_state['message']}")
            st.markdown(f"#### 🔥 Login Streak: **{plant_state['streak']} days**")

            st.markdown("<br>", unsafe_allow_html=True)

            if plant_state.get("can_replant"):
                if st.button("🌱 Plant seed again", type="secondary"):
                    # 🔥 log real replant event
                    log_event("plant", "replanted")

                    # 🔁 refresh backend-derived plant state
                    st.session_state["_force_plant_refresh"] = datetime.now(IST).isoformat()

                    st.success("A new seed has been planted 🌱 Come back tomorrow!")
                    st.rerun()
    else:
        st.info("🌱 Your plant will appear once you start your journey!")

st.divider()


# ---------------- Guides ---------------- #
st.subheader("📖 Feature Guides")

cols = st.columns(len(FEATURE_GUIDES))

for idx, (key, data) in enumerate(FEATURE_GUIDES.items()):
    with cols[idx]:

        if st.button(
            f"🎯 {data['title']}\n\n{data['subtitle']}",
            key=f"guide_btn_{key}",
            use_container_width=True
        ):
            log_event("guides", "open_from_dashboard", {"guide": key})
            st.session_state.selected_guide = key
            st.switch_page("pages/guides.py")

st.divider()



# ---------------- Quiz Popup / Timer ---------------- #
if quiz_completed:
    st.subheader("⏳ Next Quiz Available In")

    resp = requests.get(f"{API_BASE_URL}/quizzes/next-available", headers=headers)
    if resp.status_code == 200:
        remaining = resp.json()["seconds_remaining"]
        timer = st.empty()

        while remaining > 0:
            h, r = divmod(remaining, 3600)
            m, s = divmod(r, 60)
            timer.metric("Next Daily Quiz", f"{h:02d}:{m:02d}:{s:02d}")
            time.sleep(1)
            remaining -= 1
else:
    with st.container(border=True):
        st.markdown("### 🎯 Daily Training Available")
        st.write(f"Hello **{user['name']}**! Ready to earn points today?")
        col1, col2 = st.columns([1, 4])

        with col1:
            if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
                log_event("dashboard", "start_quiz_click")
                st.switch_page("pages/quizzes.py")

        with col2:
            if st.button("🕒 Maybe Later", use_container_width=True):
                log_event("dashboard", "maybe_later_click")
                st.rerun()

st.divider()
