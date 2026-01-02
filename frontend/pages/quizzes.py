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
    """
    Fetch all questions of a given type and return one random question
    """
    response = requests.get(
        f"{API_BASE_URL}/questions/",
        params={"question_type": question_type},
        timeout=5,
    )
    response.raise_for_status()
    questions = response.json()
    return random.choice(questions)


def initialize_quiz():
    """
    Initialize quiz with exactly 3 questions:
    Role, Plan, Sugarcane
    """
    st.session_state.quiz_questions = [
        fetch_random_question("Role"),
        fetch_random_question("Plan"),
        fetch_random_question("Sugarcane"),
    ]
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.completed = False


# ------------------ Page Header ------------------ #

st.title("🧪 Daily Quiz")


# ------------------ Initialize State ------------------ #

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

    # log analytics event
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

    # move to next question or finish
    if idx < 2:
        st.session_state.current_index += 1
        st.experimental_rerun()
    else:
        st.session_state.completed = True


# ------------------ Quiz Completed ------------------ #

if st.session_state.get("completed"):
    st.success("🎉 Quiz Completed!")
    st.markdown(f"### 🏆 Your Score: {st.session_state.score} / 30")

    if st.button("Go to Dashboard"):
        # clear quiz-related session state
        for key in ["quiz_questions", "current_index", "score", "completed"]:
            st.session_state.pop(key, None)

        st.switch_page("pages/dashboard.py")

