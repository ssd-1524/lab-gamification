from __future__ import annotations

from typing import Dict, List
import random
import requests
import streamlit as st

from utils.sessions import get_access_token, is_authenticated
from utils.api_client import log_event

API_BASE_URL = "http://localhost:8000"

# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")

# ------------------ Helpers ------------------ #

def fetch_random_question(question_type: str) -> Dict:
    response = requests.get(
        f"{API_BASE_URL}/questions/",
        params={"question_type": question_type},
        timeout=5,
    )
    response.raise_for_status()
    return random.choice(response.json())


def check_daily_quiz_status() -> bool:
    """Check once per session whether today's quiz is completed"""
    token = get_access_token()
    if not token:
        return True

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{API_BASE_URL}/quizzes/status",
        headers=headers,
        timeout=5,
    )

    if response.status_code == 200:
        return response.json().get("completed", False)

    return True


def initialize_quiz():
    st.session_state.quiz_questions = [
        fetch_random_question("Role"),
        fetch_random_question("Plan"),
        fetch_random_question("Sugarcane"),
    ]
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.completed = False
    st.session_state.points_saved = False


def submit_quiz_score(score: int):
    token = get_access_token()
    if not token:
        st.error("Authentication token missing.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{API_BASE_URL}/quizzes/complete",
        json={"score": score},
        headers=headers,
        timeout=5,
    )

    if response.status_code != 200:
        st.error("Failed to save quiz score")

# ------------------ Page Header ------------------ #

st.title("🧪 Daily Quiz")

# ------------------ Daily Quiz Lock (ONCE) ------------------ #

if "daily_quiz_completed" not in st.session_state:
    st.session_state.daily_quiz_completed = check_daily_quiz_status()

if st.session_state.daily_quiz_completed:
    st.warning("🚫 Daily Quiz is Already Completed")
    st.stop()

# ------------------ Initialize Quiz ------------------ #

if "quiz_questions" not in st.session_state:
    initialize_quiz()

questions: List[Dict] = st.session_state.quiz_questions
idx: int = st.session_state.current_index
current_question: Dict = questions[idx]

# ------------------ Render Question ------------------ #

st.markdown(f"### Question {idx + 1} of 3")
st.write(current_question["question_text"])

options_map = {
    "A": current_question["option_a"],
    "B": current_question["option_b"],
    "C": current_question["option_c"],
}

with st.form(key=f"quiz_form_{idx}"):
    selected_label = st.radio(
        "Choose an option:",
        options=list(options_map.keys()),
        format_func=lambda k: f"{k}. {options_map[k]}",
    )
    submitted = st.form_submit_button("Submit")

# ------------------ Submission Logic ------------------ #

if submitted:
    correct = selected_label == current_question["correct_option"]

    if correct:
        st.session_state.score += 10

    token = get_access_token()
    if token:
        log_event(
            token=token,
            payload={
                "feature": "quiz",
                "action": "answer",
                "metadata": {
                    "question_id": current_question["question_id"],
                    "question_type": current_question["question_type"],
                    "selected": selected_label,
                    "correct": correct,
                },
            },
        )

    if idx < 2:
        st.session_state.current_index += 1
    else:
        st.session_state.completed = True

# ------------------ Quiz Completed ------------------ #

if st.session_state.get("completed"):
    st.success("🎉 Quiz Completed!")
    st.markdown(f"### 🏆 Your Score: {st.session_state.score} / 30")

    if not st.session_state.points_saved:
        submit_quiz_score(st.session_state.score)
        st.session_state.points_saved = True
        st.session_state.daily_quiz_completed = True

    if st.button("Go to Dashboard"):
        for key in [
            "quiz_questions",
            "current_index",
            "score",
            "completed",
            "points_saved",
            "daily_quiz_completed",
        ]:
            st.session_state.pop(key, None)

        st.switch_page("pages/dashboard.py")
