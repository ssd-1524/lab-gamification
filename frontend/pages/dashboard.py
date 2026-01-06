import streamlit as st
import time
import requests

from utils.api_client import get_user_points
from utils.events import log_event
from utils.sessions import get_access_token
from utils.ui_utils import FEATURE_GUIDES, inject_apple_styles



API_BASE_URL = "http://localhost:8000"

# 1. Page Configuration
st.set_page_config(page_title="Dashboard - Stomata Labs", page_icon="📊", layout="wide")
inject_apple_styles()


# 2. Security Check
if not st.session_state.get("is_authenticated"):
    st.warning("Please login to access the dashboard.")
    st.switch_page("streamlit_app.py")
    st.stop()

# 🔴 PAGE VIEW EVENT
log_event("dashboard", "page_view")

# 3. Data Initialization
user = st.session_state.user
points_data = get_user_points()

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ------------------ QUIZ STATUS ------------------ #
quiz_status_resp = requests.get(f"{API_BASE_URL}/quizzes/status", headers=headers)
quiz_completed = quiz_status_resp.json().get("completed", False) if quiz_status_resp.status_code == 200 else False

# ------------------ MAIN DASHBOARD UI ------------------ #
st.title(f"👋 Welcome, {user['name']}!")

st.info(
    f"📍 **Location:** {user.get('loc_name', 'Not Assigned')} | "
    f"🛠️ **Role:** {user.get('role_name', 'General User')}"
)

st.divider()

# 4. Key Metrics
streak_resp = requests.get("http://localhost:8000/sessions/streak", headers=headers)
streak = streak_resp.json().get("streak", 0) if streak_resp.status_code == 200 else 0

st.metric("🔥 Login Streak", f"{streak} days")

rank_resp = requests.get(
    "http://localhost:8000/users/me/rank",
    headers=headers,
)

rank_data = rank_resp.json() if rank_resp.status_code == 200 else {}


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Points",
        value=f"{points_data.get('total_points', 0)} pts",
        delta="Lifetime Earnings",
    )
    log_event("wallet", "view", {"total_points": points_data.get("total_points", 0)})

with col2:
    pos = rank_data.get("position")
    st.metric("Rank", f"{pos}" if pos else "—")

with col3:
    st.metric(
        label="Current Tier",
        value=rank_data.get("rank") or "—",
    )

    if rank_data.get("badge_image"):
        st.image(rank_data["badge_image"], width=48)

st.divider()

# 5. Action Center
st.subheader("🎯 Active Challenges")
c1, c2 = st.columns([3, 1])

with c1:
    st.markdown(
        """
        ### Sugarcane
        Your contribution helps improve our detection models, earns you points and
        helps increase our production.
        """
    )

with c2:
    if st.button("Open Training Center", use_container_width=True, type="primary"):
        log_event("dashboard", "open_training_center")
        st.switch_page("pages/quizzes.py")


st.subheader("📖 Feature Guides")

cols = st.columns(len(FEATURE_GUIDES))

for idx, (key, data) in enumerate(FEATURE_GUIDES.items()):
    with cols[idx]:
        card_label = f"🎯 {data['title']}\n{data['subtitle']}"

        if st.button(card_label, key=f"guide_btn_{key}", use_container_width=True):
            log_event("guides", "open_from_dashboard", {"guide": key})
            st.session_state.selected_guide = key
            st.switch_page("pages/guides.py")
st.divider()

# ------------------ QUIZ LOCK + TIMER ------------------ #
if quiz_completed:
    st.subheader("⏳ Next Quiz Available In")

    resp = requests.get(f"{API_BASE_URL}/quizzes/next-available", headers=headers)
    if resp.status_code == 200:
        remaining = resp.json()["seconds_remaining"]
        timer_placeholder = st.empty()

        while remaining > 0:
            hrs, rem = divmod(remaining, 3600)
            mins, secs = divmod(rem, 60)
            timer_placeholder.metric(
                label="Next Daily Quiz",
                value=f"{hrs:02d}:{mins:02d}:{secs:02d}",
            )
            time.sleep(1)
            remaining -= 1
    else:
        st.info("Next quiz countdown unavailable.")
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