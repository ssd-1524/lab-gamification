import streamlit as st
from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event
import requests

API = "http://localhost:8000"

st.set_page_config(
    page_title="Stomata Labs Gamification",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide sidebar completely before authentication
if not is_authenticated():
    st.markdown("""
        <style>
        section[data-testid="stSidebar"],
        button[kind="header"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state
st.session_state.setdefault("is_authenticated", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("access_token", None)

# -------- Sidebar -------- #
if is_authenticated():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    plan = None

    try:
        plan_resp = requests.get(f"{API}/users/me/plan", headers=headers)
        plan = plan_resp.json().get("plan_name")
    except:
        pass

    with st.sidebar:
        st.markdown("## 🧪 Stomata Labs")

        if st.button("📊 Dashboard"):
            log_event("sidebar", "dashboard_click")
            st.switch_page("pages/dashboard.py")

        if st.button("🧪 Daily Quiz"):
            log_event("sidebar", "quiz_click")
            st.switch_page("pages/quizzes.py")

        if st.button("🏆 Leaderboard"):
            log_event("sidebar", "leaderboard_click")
            st.switch_page("pages/leaderboard.py")

        if st.button("📖 Guides"):
            log_event("sidebar", "guides_click")
            st.switch_page("pages/guides.py")

        if st.button("👤 Profile"):
            log_event("sidebar", "profile_click")
            st.switch_page("pages/profile.py")

        if plan in ("Prime", "Nexus"):
            if st.button("🚨 Anomaly Detection"):
                log_event("sidebar", "anomaly_click")
                st.switch_page("pages/anomaly_detection.py")

        if plan == "Nexus":
            if st.button("⚙️ Optimizer"):
                log_event("sidebar", "optimizer_click")
                st.switch_page("pages/optimizer.py")

# -------- Main Page -------- #
st.title("🌱 Welcome to Stomata Labs")
st.subheader("Unlock the Agro-Industrial Potential of the Sugar Industry with AI")

if st.session_state.is_authenticated:
    st.success(f"Welcome back, {st.session_state.user['name']}!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to My Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")

    with col2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.user = None
            st.session_state.access_token = None
            st.rerun()

else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login / Sign Up", type="primary", use_container_width=True):
            st.switch_page("pages/auth.py")
    with col2:
        if st.button("Learn More", use_container_width=True):
            st.markdown("This platform helps sugar mill teams improve performance through AI-driven training.")
