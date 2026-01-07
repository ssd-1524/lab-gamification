# frontend/pages/auth.py
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

# 1. Fetch data at the TOP of the file (Outside of any logic)
roles_data = get_roles() or []
locations_data = get_locations() or []

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
                res = login_user(login_payload)

                if "access_token" in res:
                    set_authenticated(token=res["access_token"], user=res["user"])
                    log_event("auth", "login_success")  # 🔴 ADDED

                    st.session_state.show_login_popup = True
                    st.success(f"Welcome back, {res['user']['name']}!")
                    st.switch_page("pages/dashboard.py")
                else:
                    log_event(
                        "auth",
                        "login_failed",
                        {"reason": res.get("detail", "unknown")},
                    )  # 🔴 ADDED
                    st.error(res.get("detail", "Login failed. Check your credentials."))

# --- SIGNUP SECTION ---
with tab_signup:
    with st.form("signup_form"):
        st.subheader("Register New Account")
        name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        selected_role = st.selectbox(
            "Your Role",
            options=roles_data,
            format_func=lambda x: x["role_name"] if x else "No roles available",
        )

        # Show location + plan_type together for clarity
        def _loc_format(x):
            if not x:
                return "No locations available"
            plan_type = x.get("plan_type")
            if plan_type:
                return f"{x.get('loc_name', '')} — {plan_type}"
            return x.get("loc_name", "")

        selected_location = st.selectbox(
            "Primary Location",
            options=locations_data,
            format_func=_loc_format,
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
                res = signup_user(signup_payload)

                if res.get("status") == "success":
                    log_event("auth", "signup_success")  # 🔴 ADDED
                    st.success("Account created! You can now log in.")
                else:
                    log_event(
                        "auth",
                        "signup_failed",
                        {"reason": res.get("detail", "unknown")},
                    )  # 🔴 ADDED
                    st.error(f"Signup failed: {res.get('detail')}")
