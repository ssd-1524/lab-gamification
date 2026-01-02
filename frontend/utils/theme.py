from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply black and neon-green theme across the app."""
    st.markdown(
        """
        <style>
        html, body, [class*="stApp"] {
            background-color: #050505;
            color: #00ff7f;
        }

        h1, h2, h3, h4 {
            color: #00ff7f;
        }

        .stButton>button {
            background-color: #050505;
            color: #00ff7f;
            border: 1px solid #00ff7f;
            border-radius: 8px;
            box-shadow: 0 0 8px #00ff7f;
        }

        .stButton>button:hover {
            background-color: #00ff7f;
            color: #050505;
        }

        .stTextInput>div>div>input,
        .stSelectbox>div>div>div {
            background-color: #050505;
            color: #00ff7f;
            border: 1px solid #00ff7f;
        }

        .stMetric {
            background-color: #050505;
            border: 1px solid #00ff7f;
            box-shadow: 0 0 10px #00ff7f;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
