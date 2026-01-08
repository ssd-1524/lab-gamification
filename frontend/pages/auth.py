import streamlit as st
from utils.api_client import get_roles, get_locations, signup_user, login_user
from utils.sessions import set_authenticated, is_authenticated

from utils.events import log_event  # 🔴 ADDED

st.set_page_config(page_title="Auth - Stomata Labs", page_icon="🔐")

# 🔐 HIDE SIDEBAR IF NOT AUTHENTICATED
if not is_authenticated():
    st.markdown(
        """
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

# Initialize session state for lazy-loaded data
if "roles_data" not in st.session_state:
    st.session_state.roles_data = []
if "locations_data" not in st.session_state:
    st.session_state.locations_data = []
if "roles_loaded" not in st.session_state:
    st.session_state.roles_loaded = False
if "locations_loaded" not in st.session_state:
    st.session_state.locations_loaded = False

st.title("🔐 Authentication")

tab_login, tab_signup = st.tabs(["Login", "Create Account"])

# --- LOGIN SECTION ---
with tab_login:
    with st.form("login_form"):
        st.subheader("Sign In")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login", use_container_width=True)

        if submit_login:
            log_event("auth", "login_click")  # 🔴 ADDED

            if not email or not password:
                log_event("auth", "login_failed", {"reason": "missing_fields"})  # 🔴 ADDED
                st.error("Please fill in all fields.")
            else:
                login_payload = {"email": email, "password": password}
                try:
                    res = login_user(login_payload)
                except Exception as e:
                    log_event("auth", "login_error", {"error": str(e)})
                    st.warning("Backend unavailable or timed out. Please try again in a moment.")
                    st.stop()

                if isinstance(res, dict) and "access_token" in res:
                    set_authenticated(token=res["access_token"], user=res["user"])
                    log_event("auth", "login_success")  # 🔴 ADDED

                    st.session_state.show_login_popup = True
                    st.success(f"Welcome back, {res['user']['name']}!")
                    st.switch_page("pages/dashboard.py")
                else:
                    log_event(
                        "auth",
                        "login_failed",
                        {"reason": res.get("detail", "unknown") if isinstance(res, dict) else str(res)},
                    )  # 🔴 ADDED
                    st.error(res.get("detail", "Login failed. Check your credentials.") if isinstance(res, dict) else "Login failed. Check your credentials.")

# --- SIGNUP SECTION ---
with tab_signup:
    with st.form("signup_form"):
        st.subheader("Register New Account")
        name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        # Lazy-load roles & locations only when user requests
        if not st.session_state.roles_loaded or not st.session_state.locations_loaded:
            if st.button("Load roles & locations"):
                log_event("auth", "load_roles_clicked")
                with st.spinner("Loading roles and locations..."):
                    try:
                        roles = get_roles() or []
                        locations = get_locations() or []

                        st.session_state.roles_data = roles
                        st.session_state.locations_data = locations
                        st.session_state.roles_loaded = True
                        st.session_state.locations_loaded = True

                        log_event("auth", "load_roles_success")
                    except Exception as e:
                        log_event("auth", "load_roles_failed", {"error": str(e)})
                        st.error("Failed to load roles or locations. Please try again in a moment.")

        # Display selectboxes (disabled if not loaded)
        def _role_format(x):
            return x.get("role_name") if x else "No roles available"

        selected_role = None
        if st.session_state.roles_loaded and st.session_state.roles_data:
            selected_role = st.selectbox(
                "Your Role",
                options=st.session_state.roles_data,
                format_func=_role_format,
                key="select_role",
            )
        else:
            st.info("Click 'Load roles & locations' to populate role & location lists.")

        # Show location + plan_type together for clarity
        def _loc_format(x):
            if not x:
                return "No locations available"
            plan_type = x.get("plan_type")
            if plan_type:
                return f"{x.get('loc_name', '')} — {plan_type}"
            return x.get("loc_name", "")

        selected_location = None
        if st.session_state.locations_loaded and st.session_state.locations_data:
            selected_location = st.selectbox(
                "Primary Location",
                options=st.session_state.locations_data,
                format_func=_loc_format,
                key="select_location",
            )

        submit_signup = st.form_submit_button("Sign Up", use_container_width=True)

        if submit_signup:
            log_event("auth", "signup_click")  # 🔴 ADDED

            if not all([name, new_email, new_password, selected_role, selected_location]):
                log_event("auth", "signup_failed", {"reason": "missing_fields"})  # 🔴 ADDED
                st.error("Please fill in all fields.")
            else:
                # selected_role and selected_location are dicts returned from the API
                signup_payload = {
                    "name": name,
                    "email": new_email,
                    "password": new_password,
                    "role_id": selected_role["role_id"],
                    "loc_id": selected_location["loc_id"],
                }
                try:
                    res = signup_user(signup_payload)
                except Exception as e:
                    log_event("auth", "signup_error", {"error": str(e)})
                    st.warning("Backend unavailable or timed out. Please try again in a moment.")
                    st.stop()

                if isinstance(res, dict) and res.get("status") == "success":
                    log_event("auth", "signup_success")  # 🔴 ADDED
                    st.success("Account created! You can now log in.")
                else:
                    log_event(
                        "auth",
                        "signup_failed",
                        {"reason": res.get("detail", "unknown") if isinstance(res, dict) else str(res)},
                    )  # 🔴 ADDED
                    st.error(f"Signup failed: {res.get('detail') if isinstance(res, dict) else str(res)}")