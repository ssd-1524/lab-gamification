from __future__ import annotations

import requests
import streamlit as st
from datetime import datetime
from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event

API_BASE = "http://localhost:8000"

# ---------------- Guards ---------------- #
if not is_authenticated():
    st.switch_page("pages/auth.py")

st.set_page_config(page_title="Anomaly Detection", layout="wide")

log_event("anomaly", "page_view")

st.title("🚨 Anomaly Detection")

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Fetch Stream ---------------- #
resp = requests.get(f"{API_BASE}/anomaly/stream", headers=headers)

if resp.status_code != 200:
    st.error("Unable to load anomaly stream.")
    st.stop()

data = resp.json()
values = [d["value"] for d in data]
timestamps = [d["ts"] for d in data]

st.line_chart({"Sensor Value": values})

latest = values[-1]

# ---------------- Anomaly Detection Tracking ---------------- #
if "anomaly_start_ts" not in st.session_state:
    st.session_state.anomaly_start_ts = None

if latest > 80:
    if st.session_state.anomaly_start_ts is None:
        st.session_state.anomaly_start_ts = datetime.utcnow()

        log_event(
            "anomaly",
            "detected",
            {"value": latest},
        )

# ---------------- Mock Recommendation ---------------- #
if latest > 95:
    severity = "High"
    points = 20
elif latest > 80:
    severity = "Medium"
    points = 10
else:
    severity = "Low"
    points = 5

st.subheader("⚠️ Recommendation")
st.write(f"Detected **{severity}** severity anomaly. Suggested action: *Reset process valve*.")

col1, col2 = st.columns(2)

with col1:
    if st.button(f"Resolve Anomaly (+{points} pts)"):
        detected_at = st.session_state.anomaly_start_ts
        resolved_at = datetime.utcnow()

        response_time = None
        if detected_at:
            response_time = (resolved_at - detected_at).total_seconds()

        log_event(
            "anomaly",
            "resolved",
            {
                "severity": severity,
                "response_time_sec": response_time,
            },
        )

        requests.post(
            f"{API_BASE}/bonus/reward",
            headers=headers,
            json={
                "feature": "anomaly",
                "points": points,
                "metadata": {
                    "severity": severity,
                    "response_time_sec": response_time,
                },
            },
        )

        st.session_state.anomaly_start_ts = None
        st.success(f"Bonus +{points} points awarded!")

with col2:
    if st.button("Ignore"):
        log_event("anomaly", "ignored", {"severity": severity})
        st.session_state.anomaly_start_ts = None
        st.info("Anomaly ignored.")
