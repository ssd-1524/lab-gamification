from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.api_client import log_event
from utils.sessions import get_access_token, is_authenticated


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")


# ------------------ Page Header ------------------ #

st.title("🧪 Daily Quizzes")


# ------------------ Fetch Quiz (Placeholder) ------------------ #

def _fetch_quiz() -> Dict[str, Any]:
    return {
        "question": "What does API stand for?",
        "options": [
            "Application Programming Interface",
            "Advanced Program Input",
            "Automated Processing Instruction",
        ],
        "answer": "Application Programming Interface",
    }


quiz: Dict[str, Any] = _fetch_quiz()

st.markdown("### 📘 Today's Question")
st.write(quiz["question"])

with st.form("daily_quiz_form"):
    choice = st.radio("Select your answer:", quiz["options"])
    submitted = st.form_submit_button("Submit")


if submitted:
    correct = choice == quiz["answer"]
    points = 30 if correct else 0

    payload: Dict[str, Any] = {
        "feature": "daily_quiz",
        "action": "submit",
        "metadata": {"correct": correct, "points": points},
    }

    token = get_access_token()
    if token:
        log_event(token=token, payload=payload)

    if correct:
        st.success("Correct! You earned 30 points 🎉")
    else:
        st.warning("Incorrect answer. Try again tomorrow!")
