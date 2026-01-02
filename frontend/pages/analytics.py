from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from utils.session import get_current_user, is_authenticated


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")

user = get_current_user()
if not user or user.get("role") not in {"Admin", "HR"}:
    st.error("You are not authorized to view this page.")
    st.stop()


# ------------------ Page Header ------------------ #

st.title("📊 Platform Analytics")


# ------------------ Placeholder Analytics ------------------ #

def _fetch_usage_metrics() -> List[Dict[str, Any]]:
    return [
        {"metric": "Total Logins", "value": 1250},
        {"metric": "Quizzes Completed", "value": 980},
        {"metric": "Badges Awarded", "value": 150},
    ]


metrics = _fetch_usage_metrics()

st.markdown("### 📈 Usage Metrics")

for item in metrics:
    st.metric(label=item["metric"], value=item["value"])
