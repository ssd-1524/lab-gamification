from __future__ import annotations

from typing import Iterable

import streamlit as st

from utils.sessions import get_current_user, is_authenticated


def require_authentication() -> None:
    """Ensure user is authenticated before accessing the page."""
    if not is_authenticated():
        st.switch_page("pages/auth.py")


def require_roles(allowed_roles: Iterable[str]) -> None:
    """Restrict access to users with specific roles."""
    user = get_current_user()
    if not user or user.get("role") not in set(allowed_roles):
        st.error("You do not have permission to access this page.")
        st.stop()


def require_plan(allowed_plans: Iterable[str]) -> None:
    """Restrict access based on subscription plan."""
    user = get_current_user()
    if not user or user.get("plan") not in set(allowed_plans):
        st.error("Your subscription plan does not allow access to this feature.")
        st.stop()
