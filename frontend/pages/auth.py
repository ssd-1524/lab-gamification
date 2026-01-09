import streamlit as st
from utils.api_client import get_roles, get_locations, signup_user, login_user
from utils.sessions import set_authenticated, is_authenticated
from utils.events import log_event
from utils.theme import apply_theme

st.set_page_config(page_title="Auth - Stomata Labs", page_icon="🔐")
apply_theme()
# -------- Auto-load roles & locations once --------
if not st.session_state.get("roles_loaded"):
    try:
        st.session_state.roles_data = get_roles() or []
        st.session_state.roles_loaded = True
    except Exception:
        st.session_state.roles_data = []
        st.session_state.roles_loaded = False

if not st.session_state.get("locations_loaded"):
    try:
        st.session_state.locations_data = get_locations() or []
        st.session_state.locations_loaded = True
    except Exception:
        st.session_state.locations_data = []
        st.session_state.locations_loaded = False


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
            log_event("auth", "login_click")

            if not email or not password:
                log_event("auth", "login_failed", {"reason": "missing_fields"})
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
                    log_event("auth", "login_success")

                    st.session_state.show_login_popup = True
                    st.success(f"Welcome back, {res['user'].get('name', 'User')}!")

                    # 🔁 HARD NAVIGATION FIX
                    st.switch_page("pages/dashboard.py")

                else:
                    reason = res.get("detail", "unknown") if isinstance(res, dict) else str(res)
                    log_event("auth", "login_failed", {"reason": reason})
                    st.error(res.get("detail", "Login failed. Check your credentials.") if isinstance(res, dict) else "Login failed. Check your credentials.")

# --- SIGNUP SECTION ---
with tab_signup:

    with st.form("signup_form"):
        st.subheader("Register New Account")
        name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        # Role selectbox (uses loaded session state)
        def _role_format(x):
            return x.get("role_name") if x else ""

        role_options = st.session_state.roles_data if st.session_state.roles_loaded else []

        selected_role = st.selectbox(
            "Your Role",
            options=role_options,
            format_func=_role_format,
            disabled=not st.session_state.roles_loaded,
            placeholder="Click 'Load roles & locations' to populate",
            key="select_role",
        )

        # Show location + plan_type together for clarity
        def _loc_format(x):
            if not x:
                return ""
            plan = x.get("plan_type")
            return f"{x.get('loc_name', '')} — {plan}" if plan else x.get("loc_name", "")

        location_options = st.session_state.locations_data if st.session_state.locations_loaded else []

        selected_location = st.selectbox(
            "Primary Location",
            options=location_options,
            format_func=_loc_format,
            disabled=not st.session_state.locations_loaded,
            placeholder="Click 'Load roles & locations' to populate",
            key="select_location",
        )


        submit_signup = st.form_submit_button("Sign Up", use_container_width=True)

        if submit_signup:
            log_event("auth", "signup_click")

            if not all([name, new_email, new_password, selected_role, selected_location]):
                log_event("auth", "signup_failed", {"reason": "missing_fields"})
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
                    log_event("auth", "signup_success")

                    # 🔐 AUTO LOGIN AFTER SIGNUP
                    try:
                        login_res = login_user({"email": new_email, "password": new_password})
                    except Exception as e:
                        st.error("Signup successful, but auto-login failed. Please login manually.")
                        st.stop()

                    if isinstance(login_res, dict) and "access_token" in login_res:
                        set_authenticated(token=login_res["access_token"], user=login_res["user"])
                        log_event("auth", "signup_auto_login_success")
                        st.success(f"Welcome, {login_res['user'].get('name', 'User')}!")
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error("Signup succeeded but auto-login failed. Please login.")

                else:
                    reason = res.get("detail", "unknown") if isinstance(res, dict) else str(res)
                    log_event("auth", "signup_failed", {"reason": reason})
                    st.error(f"Signup failed: {res.get('detail') if isinstance(res, dict) else str(res)}")