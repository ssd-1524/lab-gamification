import streamlit as st

def apply_theme() -> None:
    st.markdown("""
    <style>
    /* -------- Base button -------- */
    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.55rem 1.1rem !important;
        box-shadow: none !important;
    }

    /* -------- Hover -------- */
    div.stButton > button:hover {
        background-color: #1f1f1f !important;
        color: #ffffff !important;
    }

    /* -------- Focus / Active -------- */
    div.stButton > button:focus,
    div.stButton > button:active {
        background-color: #000000 !important;
        color: #ffffff !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(0,0,0,0.25) !important;
    }

    /* -------- Disabled -------- */
    div.stButton > button:disabled {
        background-color: #3a3a3a !important;
        color: #d1d1d1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
