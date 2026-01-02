from __future__ import annotations

import streamlit as st


def show_popup(title: str, message: str, *, icon: str = "🎉", key: str) -> None:
    """Render a modal-style popup card.

    Args:
        title: Popup title text.
        message: Popup message.
        icon: Emoji icon for the popup.
        key: Session state key controlling popup visibility.
    """
    if not st.session_state.get(key):
        return

    st.markdown(
        f"""
        <style>
        .popup-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 1000;
        }}
        .popup-card {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #ffffff;
            padding: 24px;
            border-radius: 14px;
            width: 420px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.2);
            z-index: 1001;
        }}
        </style>

        <div class="popup-overlay"></div>
        <div class="popup-card">
            <h2>{icon} {title}</h2>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Close", key=f"{key}_close"):
        st.session_state[key] = False
