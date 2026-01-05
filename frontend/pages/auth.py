import streamlit as st
from utils.api_client import get_roles, get_locations, signup_user, login_user
from utils.sessions import set_authenticated

st.set_page_config(page_title="Auth - Stomata Labs", page_icon="🔐")

# 1. Fetch data at the TOP of the file (Outside of any logic)
# This ensures dropdowns populate immediately when the page loads
roles_data = get_roles()
locations_data = get_locations()

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
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                # FIX: Send as a dictionary to match api_client update
                login_payload = {"email": email, "password": password}
                res = login_user(login_payload)
                
                if "access_token" in res:
                    set_authenticated(
                        token=res["access_token"],
                        user=res["user"]
                    )
                    st.session_state.show_login_popup = True  # Trigger dashboard popup
                    
                    st.success(f"Welcome back, {res['user']['name']}!")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error(res.get("detail", "Login failed. Check your credentials."))

# --- SIGNUP SECTION ---
with tab_signup:
    with st.form("signup_form"):
        st.subheader("Register New Account")
        name = st.text_input("Full Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        # Dropdowns
        selected_role = st.selectbox(
            "Your Role",
            options=roles_data,
            format_func=lambda x: x["role_name"] if x else "No roles available"
        )

        selected_location = st.selectbox(
            "Primary Location",
            options=locations_data,
            format_func=lambda x: x["loc_name"] if x else "No locations available"
        )

        submit_signup = st.form_submit_button("Sign Up", use_container_width=True)

        if submit_signup:
            if not all([name, new_email, new_password, selected_role, selected_location]):
                st.error("Please fill in all fields.")
            else:
                signup_payload = {
                    "name": name,
                    "email": new_email,
                    "password": new_password,
                    "role_id": selected_role["role_id"],
                    "loc_id": selected_location["loc_id"]
                }
                res = signup_user(signup_payload)
                if res.get("status") == "success":
                    st.success("Account created! You can now log in.")
                else:
                    st.error(f"Signup failed: {res.get('detail')}")