from __future__ import annotations

import time
import requests
import streamlit as st
from datetime import datetime
import pytz

from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Anomaly Detection", layout="wide")

# ---------------- Guards ---------------- #
if not is_authenticated():
    st.switch_page("pages/auth.py")

log_event("anomaly", "page_view")
st.title("🚨 Anomaly Detection – Live Feed")

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Session State ---------------- #
if "anomaly_active" not in st.session_state:
    st.session_state.anomaly_active = False

if "anomaly_start_ts" not in st.session_state:
    st.session_state.anomaly_start_ts = None

if "anomaly_event_id" not in st.session_state:
    st.session_state.anomaly_event_id = None

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

chart_box = st.empty()
rec_box = st.empty()
status_box = st.empty()

# ---------------- Refresh Gate ---------------- #
if time.time() - st.session_state.last_refresh < 10:
    time.sleep(1)
    st.stop()

st.session_state.last_refresh = time.time()

# ---------------- Fetch Stream ---------------- #
resp = requests.get(f"{API_BASE}/anomaly/stream", headers=headers)

if resp.status_code == 403:
    status_box.error("Upgrade to Prime or Nexus to access Anomaly Detection.")
    st.stop()

if resp.status_code != 200:
    status_box.error("Unable to load anomaly stream.")
    st.stop()

data = resp.json()
values = [x["value"] for x in data]

with chart_box:
    st.line_chart({"Sensor Value": values})

latest = values[-1]

# ---------------- Anomaly State Machine ---------------- #
if latest > 80 and not st.session_state.anomaly_active:
    st.session_state.anomaly_active = True
    st.session_state.anomaly_start_ts = datetime.now(IST)
    st.session_state.anomaly_event_id = int(st.session_state.anomaly_start_ts.timestamp())

    log_event("anomaly", "detected", {"value": latest})

# ---------------- Recommendation Logic ---------------- #
if st.session_state.anomaly_active:
    if latest > 95:
        severity, points = "High", 20
    else:
        severity, points = "Medium", 10

    anomaly_key = st.session_state.anomaly_event_id

    with rec_box.container(border=True):
        st.subheader("⚠️ Recommendation")
        st.write(f"Detected **{severity}** anomaly. Suggested action: *Reset process valve*.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Resolve Anomaly (+{points} pts)", key=f"resolve_{anomaly_key}"):
                resolved_at = datetime.now(IST)
                detected_at = st.session_state.anomaly_start_ts

                response_time = (
                    (resolved_at - detected_at).total_seconds()
                    if detected_at else None
                )

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

                st.session_state.anomaly_active = False
                st.session_state.anomaly_start_ts = None
                st.session_state.anomaly_event_id = None
                st.success(f"Bonus +{points} points awarded!")

        with col2:
            if st.button("Ignore", key=f"ignore_{anomaly_key}"):
                log_event("anomaly", "ignored", {"severity": severity})
                st.session_state.anomaly_active = False
                st.session_state.anomaly_start_ts = None
                st.session_state.anomaly_event_id = None
                st.info("Anomaly ignored.")

# ---------------- Auto Refresh ---------------- #
time.sleep(1)
st.rerun()
