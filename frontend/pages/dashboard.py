import streamlit as st
from utils.api_client import get_user_points
from utils.events import log_event   # 🔴 ADDED

# 1. Page Configuration
st.set_page_config(page_title="Dashboard - Stomata Labs", page_icon="📊", layout="wide")

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

# --- REVISED POPUP ---
if st.session_state.get("show_login_popup", False):
    with st.container(border=True):
        st.markdown("### 🎯 Daily Training Available")
        st.write(f"Hello **{user['name']}**! We have new disease detection images for you to review today.")
        st.write("Would you like to start the quiz now and earn points?")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
                log_event("dashboard", "start_quiz_click")  # 🔴 ADDED
                st.session_state.show_login_popup = False
                st.switch_page("pages/quizzes.py")
        with col2:
            if st.button("🕒 Maybe Later", use_container_width=True):
                log_event("dashboard", "maybe_later_click")  # 🔴 ADDED
                st.session_state.show_login_popup = False
                st.rerun()
    st.divider()

# --- MAIN DASHBOARD UI ---
st.title(f"👋 Welcome, {user['name']}!")

st.info(f"📍 **Location:** {user.get('loc_name', 'Not Assigned')} | 🛠️ **Role:** {user.get('role_name', 'General User')}")

st.divider()

# 4. Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Points", 
        value=f"{points_data.get('total_points', 0)} pts",
        delta="Lifetime Earnings"
    )
    log_event("wallet", "view", {"total_points": points_data.get("total_points", 0)})  # 🔴 ADDED

with col2:
    st.metric(label="Global Rank", value="#--")

with col3:
    st.metric(
        label="Current Tier", 
        value=points_data.get('rank', 'Bronze'),
        delta="Tier Progress"
    )
    log_event("wallet", "rank_view", {"rank": points_data.get("rank", "Bronze")})  # 🔴 ADDED

st.divider()

# 5. Action Center
st.subheader("🎯 Active Challenges")
c1, c2 = st.columns([3, 1])

with c1:
    st.markdown(
        """
        ### Sugarcane & Maize Disease Training
        Your contribution helps improve our detection models. Correctly identifying 
        diseases like **Red Rot** or **Maize Dwarf Mosaic** earns you points and 
        helps protect our crops.
        """
    )
    
with c2:
    if st.button("Open Training Center", use_container_width=True, type="primary"):
        log_event("dashboard", "open_training_center")  # 🔴 ADDED
        st.switch_page("pages/quiz.py")

st.divider()

# 6. Recent Activity
st.subheader("📜 Recent Performance")
st.table([
    {"Date": "2026-01-02", "Activity": "Daily Login", "Points": "+5"},
    {"Date": "2026-01-01", "Activity": "Maize Identification", "Points": "+45"},
    {"Date": "2025-12-31", "Activity": "Sugarcane Identification", "Points": "+50"}
])
