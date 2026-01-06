import streamlit as st

def inject_apple_styles():
    """
    Theme-adaptive Apple-style stacked buttons.
    Uses Streamlit CSS variables so it auto-adapts to dark / light mode.
    """
    st.markdown("""
        <style>
        .feature-guide-root {
            color: var(--text-color);
        }

        div.stButton > button {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-left: 5px solid #ff4b4b !important;
            border-radius: 14px !important;
            padding: 18px !important;
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            min-height: 110px !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
        }

        div.stButton > button p {
            white-space: pre-line !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            line-height: 1.45 !important;
            margin: 0 !important;
        }

        div.stButton > button:hover {
            border-color: #ff4b4b !important;
            box-shadow: 0 12px 30px rgba(0,0,0,0.45) !important;
        }
        </style>
        """, unsafe_allow_html=True)



FEATURE_GUIDES = {
    "quiz": {
        "title": "Master the Daily Quiz",
        "subtitle": "Earn points by identifying lab samples correctly.",
        "steps": [
            "Navigate to the Quiz page from the sidebar.",
            "Complete the 3 daily questions tailored to your role.",
            "Watch your points update instantly."
        ]
    },
    "wallet": {
        "title": "Manage Your Wallet",
        "subtitle": "View your earnings and point history.",
        "steps": [
            "Click on the Wallet icon in the navigation bar.",
            "Check your balance and rank progress."
        ]
    },
    "leaderboard": {
        "title": "Check the Leaderboard",
        "subtitle": "Compare your progress with other members.",
        "steps": [
            "Open the Leaderboard page.",
            "Find your name and climb to the top rank."
        ]
    }
}
