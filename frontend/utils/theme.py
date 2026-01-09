import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;800&display=swap');

        /* ---------------- GLOBAL FONT OVERRIDE ---------------- */
        html, body, [class*="css"], [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"], [data-testid="stHeader"],
        .stMarkdown, .stText, .stMetric, .stButton > button,
        div, span, p, h1, h2, h3, h4, h5, h6 {
            font-family: 'Source Sans Pro', Arial, sans-serif !important;
        }

        /* ---------------- BUTTON THEME ---------------- */
        div.stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 0.55rem 1.1rem !important;
            box-shadow: none !important;
        }

        div.stButton > button:hover {
            background-color: #1f1f1f !important;
            color: #ffffff !important;
        }

        div.stButton > button:focus,
        div.stButton > button:active {
            background-color: #000000 !important;
            color: #ffffff !important;
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(0,0,0,0.25) !important;
        }

        div.stButton > button:disabled {
            background-color: #3a3a3a !important;
            color: #d1d1d1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
