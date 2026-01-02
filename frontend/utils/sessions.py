from __future__ import annotations

from typing import Any, Dict

import streamlit as st


_DEFAULT_SESSION_STATE: Dict[str, Any] = {
    "is_authenticated": False,
    "access_token": None,
    "user": None,
    "auth_mode": "login",
    "quiz_modal_pending": False,
}


def initialize_session_state() -> None:
    """Initialize required session state keys with default values."""
    for key, default in _DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default


def reset_session_state() -> None:
    """Clear authentication-related session state safely."""
    for key in _DEFAULT_SESSION_STATE:
        st.session_state[key] = _DEFAULT_SESSION_STATE[key]


def is_authenticated() -> bool:
    """Return whether the current user is authenticated."""
    return bool(st.session_state.get("is_authenticated"))


def get_access_token() -> str | None:
    """Return the stored access token, if present."""
    return st.session_state.get("access_token")


def get_current_user() -> Dict[str, Any] | None:
    """Return the logged-in user profile."""
    return st.session_state.get("user")


def set_authenticated(token: str, user: Dict[str, Any]) -> None:
    """Mark the user as authenticated and store their token and profile."""
    st.session_state["access_token"] = token
    st.session_state["user"] = user
    st.session_state["is_authenticated"] = True
    st.session_state["quiz_modal_pending"] = True


def logout() -> None:
    """Log out the user and redirect to the auth page."""
    reset_session_state()
    st.switch_page("pages/auth.py")
