import streamlit as st
from utils.sessions import is_authenticated
from utils.events import log_event

# 1. Basic Page Configuration
st.set_page_config(
    page_title="Stomata Labs Gamification",
    page_icon="🌱",
    layout="centered"
)

# 2. Initialize Session State (This persists across all pages)
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.markdown("## 🧪 Stomata Labs")

    if is_authenticated():
        if st.button("Dashboard"):
            log_event("sidebar", "dashboard_click")
            st.switch_page("pages/dashboard.py")

        if st.button("Daily Quiz"):
            log_event("sidebar", "quiz_click")
            st.switch_page("pages/quizzes.py")

        if st.button("Leaderboard"):
            log_event("sidebar", "leaderboard_click")
            st.switch_page("pages/leaderboard.py")

        if st.button("Guides"):
            log_event("sidebar", "guides_click")
            st.switch_page("pages/guides.py")

        if st.button("Profile"):
            log_event("sidebar", "profile_click")
            st.switch_page("pages/profile.py")

    else:
        if st.button("Login / Signup"):
            st.switch_page("pages/auth.py")

def main():
    # Header Section
    st.title("🌱 Welcome to Stomata Labs")
    st.subheader("Sugarcane & Maize Disease Detection Training")
    
    st.divider()

    # 3. Conditional Logic for Routing
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
                st.rerun()
                
    else:
        # User is not logged in
        st.info("Please sign in to access your training quizzes and earn points.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login / Sign Up", type="primary", use_container_width=True):
                st.switch_page("pages/auth.py")
        with col2:
            if st.button("Learn More", use_container_width=True):
                st.info("This platform helps field operators identify crop diseases through daily gamified challenges.")

    st.divider()
    
    # 4. Progress Overview (Visual Placeholder)
    st.markdown("### 🏆 Platform Rankings")
    st.caption("Top operators this week")
    st.table([
        {"Operator": "John D.", "Location": "Guatemala", "Points": 1250},
        {"Operator": "Maria S.", "Location": "Costa Rica", "Points": 1100}
    ])

if __name__ == "__main__":
    main()