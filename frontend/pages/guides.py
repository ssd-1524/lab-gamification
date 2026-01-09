from __future__ import annotations
import streamlit as st

from utils.sessions import is_authenticated
from utils.ui_utils import inject_apple_styles, FEATURE_GUIDES
from utils.theme import apply_theme


# --- Page Setup ---
st.set_page_config(page_title="Guides", layout="wide")
apply_theme()
st.markdown("<div class='feature-guide-root'>", unsafe_allow_html=True)
inject_apple_styles()

if not is_authenticated():
    st.switch_page("pages/auth.py")

guide_key = st.session_state.get("selected_guide", "quiz")
guide = FEATURE_GUIDES.get(guide_key, FEATURE_GUIDES["quiz"])

st.markdown(
    f"""
    <h2 style="color: var(--text-color); margin-bottom: 0.2em;">
        📖 Guide: {guide['title']}
    </h2>
    """,
    unsafe_allow_html=True,
)

st.divider()

# --- Content ---
for idx, step in enumerate(guide["steps"], start=1):
    st.markdown(
        f"""
        <div style="
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 10px;
            border: 5px solid rgba(0, 0, 0, 0.08);
            border-left: 5px solid #000000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        ">
            <strong>Step {idx}:</strong> {step}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# --- Bottom Navigation (Stacked Text Cards) ---
st.subheader("🎯 Discover More")

other_tips = {k: v for k, v in FEATURE_GUIDES.items() if k != guide_key}

if other_tips:
    cols = st.columns(len(other_tips))

    for idx, (key, data) in enumerate(other_tips.items()):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="font-size:16px;font-weight:700;margin-bottom:6px">
                        {data['title']}
                    </div>
                    <div style="font-size:13px;color:#475569">
                        {data['subtitle']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "Explore",
                    key=f"card_btn_{key}",
                    use_container_width=True,
                ):
                    st.session_state.selected_guide = key
                    st.rerun()
