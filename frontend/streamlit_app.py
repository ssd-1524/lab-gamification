import streamlit as st
from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event
import requests

API = "https://lab-gamification.onrender.com"


st.set_page_config(
    page_title="Stomata Labs Gamification",
    page_icon="https://hznnpqggqowmaodldfjb.supabase.co/storage/v1/object/public/images/stoma.png",
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

# -------- Main Page -------- #
st.markdown("""
<div style="display:flex;justify-content:center;margin-bottom:16px;">
    <img src="https://hznnpqggqowmaodldfjb.supabase.co/storage/v1/object/public/images/stomatalabs.png" alt="Stomata Labs Logo"
         style="height:200px;object-fit:contain;" />
</div>
""", unsafe_allow_html=True)
st.title("Welcome to Stomata Labs")
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
