from __future__ import annotations

from typing import Dict, Any

import streamlit as st

from utils.sessions import is_authenticated
from utils.api_client import get_analytics_summary
from utils.events import log_event


# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")


# 🔴 PAGE VIEW EVENT
log_event("analytics", "page_view")


# ------------------ Fetch Data ------------------ #

analytics: Dict[str, Any] = get_analytics_summary()


# ------------------ UI ------------------ #

st.title("📈 Platform Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Daily Active Users", analytics.get("daily_active_users", 0))
    log_event("analytics", "metric_view", {"metric": "daily_active_users"})

with col2:
    st.metric("Average Quiz Score", analytics.get("avg_quiz_score", 0))
    log_event("analytics", "metric_view", {"metric": "avg_quiz_score"})

with col3:
    st.metric("Total Points Issued", analytics.get("total_points_issued", 0))
    log_event("analytics", "metric_view", {"metric": "total_points_issued"})


st.divider()

st.subheader("🔥 Engagement Trends")

time_range = st.selectbox(
    "Select Time Range",
    options=["Today", "Last 7 Days", "Last 30 Days"],
)

log_event("analytics", "range_select", {"range": time_range})


if st.button("Refresh Analytics", type="primary"):
    log_event("analytics", "refresh_click")
    st.rerun()
