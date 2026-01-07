# frontend/pages/anomaly_detection.py
from __future__ import annotations

import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
from typing import List, Dict, Any, Optional

from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "http://localhost:8000"

# ========== Page config ==========
st.set_page_config(page_title="Anomaly Detection", layout="wide")

# ========== Guards ==========
if not is_authenticated():
    st.switch_page("pages/auth.py")

# ========== Auto-refresh (10s) ==========
# Change interval_ms if you want faster/slower refresh.
REFRESH_INTERVAL_MS = 10_000
if not st.session_state.get("anomaly_active"):
    st_autorefresh(interval=REFRESH_INTERVAL_MS, key="anomaly_autorefresh")

# ========== Session state (safe defaults) ==========
st.session_state.setdefault("anomaly_page_view_logged", False)
st.session_state.setdefault("anomaly_active", False)
st.session_state.setdefault("anomaly_start_ts", None)  # datetime | None
st.session_state.setdefault("anomaly_event_key", None)  # unique key for widgets
st.session_state.setdefault("anomaly_cache", {"ts": [], "values": []})
st.session_state.setdefault("last_fetch_ok", False)
st.session_state.setdefault("last_fetch_time", None)
st.session_state.setdefault("normal_since", None)  # for cooldown detection

# ========== Page view event: once per navigation ==========
if not st.session_state.anomaly_page_view_logged:
    try:
        log_event("anomaly", "page_view")
    except Exception:
        pass
    st.session_state.anomaly_page_view_logged = True

st.title("🚨 Anomaly Detection – Live Feed")

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ========== Try fetch live stream; update cache only on success ==========
fetch_error: Optional[str] = None
try:
    resp = requests.get(f"{API_BASE}/anomaly/stream", headers=headers, timeout=4)
    if resp.status_code == 403:
        st.error("Upgrade to Prime or Nexus to access Anomaly Detection.")
    elif resp.status_code != 200:
        fetch_error = f"Stream fetch failed: HTTP {resp.status_code}"
    else:
        payload = resp.json()
        fetched_values: List[int] = []
        fetched_ts: List[str] = []

        # tolerant parsing
        for item in payload:
            try:
                val = item.get("value")
                ts = item.get("ts")
                if val is None or ts is None:
                    continue
                fetched_values.append(int(val))
                fetched_ts.append(ts)
            except Exception:
                continue

        if fetched_values:
            # update cache only when we got at least one point
            st.session_state.anomaly_cache["values"] = fetched_values
            st.session_state.anomaly_cache["ts"] = fetched_ts
            st.session_state.last_fetch_ok = True
            st.session_state.last_fetch_time = datetime.now(IST).isoformat()
        else:
            fetch_error = "Stream returned no datapoints."
except requests.RequestException as e:
    fetch_error = f"Stream request error: {e}"

# ========== Use cached data (so chart never disappears) ==========
cached = st.session_state.anomaly_cache
if not cached["values"]:
    st.warning("No data available yet — waiting for first successful fetch...")
    if fetch_error:
        st.info(fetch_error)
    # keep page visible; nothing else to render yet
    st.stop()

# build DataFrame for charting (stable across reruns)
df = pd.DataFrame({"ts": cached["ts"], "value": cached["values"]})
# parse timestamps if possible; otherwise use order index
try:
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts")
except Exception:
    # leave default index if parsing fails
    pass

# Render chart (always rendered)
st.line_chart(df["value"] if "value" in df else df)

# Latest (live-edge) value
latest_value = int(df["value"].iloc[-1]) if "value" in df and not df.empty else None

# ========== Anomaly FSM (detection, cooldown, auto-clear) ==========
# thresholds
DETECT_THRESHOLD = 80
COOLDOWN_THRESHOLD = 70
COOLDOWN_SECONDS = 10

now = datetime.now(IST)

# Detect new anomaly
if latest_value is not None and latest_value > DETECT_THRESHOLD and not st.session_state.anomaly_active:
    st.session_state.anomaly_active = True
    st.session_state.anomaly_start_ts = now
    st.session_state.anomaly_event_key = int(now.timestamp())
    st.session_state.normal_since = None
    try:
        log_event("anomaly", "detected", {"value": latest_value})
    except Exception:
        pass

# Track normalization (start counting when value falls below COOLDOWN_THRESHOLD)
if st.session_state.anomaly_active:
    if latest_value is not None and latest_value < COOLDOWN_THRESHOLD:
        if st.session_state.normal_since is None:
            st.session_state.normal_since = now
    else:
        st.session_state.normal_since = None

# If normalized for long enough, auto-clear anomaly (without logging resolved)
if st.session_state.normal_since is not None:
    elapsed = (now - st.session_state.normal_since).total_seconds()
    if elapsed >= COOLDOWN_SECONDS:
        st.session_state.anomaly_active = False
        st.session_state.anomaly_start_ts = None
        st.session_state.anomaly_event_key = None
        st.session_state.normal_since = None
        # DO NOT auto-log "resolved" to avoid noisy metrics; user action logs resolved.

# ========== Recommendation UI (only while anomaly active) ==========
if st.session_state.anomaly_active:
    # severity & points mapping
    severity = "High" if latest_value is not None and latest_value > 95 else "Medium"
    points = 20 if severity == "High" else 10

    st.divider()
    st.subheader("⚠️ Recommendation")
    st.write(
        f"Detected **{severity}** anomaly (value: **{latest_value}**). "
        "Suggested action: *Reset process valve*."
    )

    detected_at = st.session_state.anomaly_start_ts
    if detected_at:
        elapsed = int((now - detected_at).total_seconds())
        st.caption(f"Anomaly active for {elapsed} sec")

    # unique keys per anomaly event to avoid DuplicateWidgetID
    event_key = st.session_state.anomaly_event_key or int(datetime.now(IST).timestamp())
    resolve_key = f"resolve_{event_key}"
    ignore_key = f"ignore_{event_key}"

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"Resolve Anomaly (+{points} pts)", key=resolve_key):
            resolved_at = datetime.now(IST)
            detected_at = st.session_state.anomaly_start_ts
            response_time = (
                (resolved_at - detected_at).total_seconds() if detected_at else None
            )

            # log resolved
            try:
                if token:
                    try:
                        requests.post(
                            f"{API_BASE}/events/",
                            headers=headers,
                            json={
                                "feature": "anomaly",
                                "action": "accepted",
                                "metadata": {
                                    "severity": severity,
                                    "response_time_sec": response_time,
                                },
                            },
                            timeout=3,
                        )
                    except Exception as e:
                        st.error("Failed to log anomaly acceptance.")
                        st.write(e)


            except Exception:
                pass

            # best-effort bonus call
            try:
                if token:
                    requests.post(
                        f"{API_BASE}/bonus/reward",
                        headers=headers,
                        json={
                            "feature": "anomaly",
                            "points": points,
                            "metadata": {"severity": severity, "response_time_sec": response_time},
                        },
                        timeout=3,
                    )
            except Exception:
                pass

            # reset FSM
            st.session_state.anomaly_active = False
            st.session_state.anomaly_start_ts = None
            st.session_state.anomaly_event_key = None
            st.session_state.normal_since = None

            st.success(f"Bonus +{points} points awarded!")

    with col2:
        if st.button("Ignore", key=ignore_key):
            try:
                log_event("anomaly", "ignored", {"severity": severity})
            except Exception:
                pass

            st.session_state.anomaly_active = False
            st.session_state.anomaly_start_ts = None
            st.session_state.anomaly_event_key = None
            st.session_state.normal_since = None
            st.info("Anomaly ignored.")

# # ========== Debug / status (optional) ==========
# with st.expander("Stream status (debug)", expanded=False):
#     st.write("Last fetch OK:", st.session_state.last_fetch_ok)
#     st.write("Last fetch time:", st.session_state.last_fetch_time)
#     if fetch_error:
#         st.write("Last fetch error:", fetch_error)
#     st.write("Cached points:", len(st.session_state.anomaly_cache["values"]))
#     # preview last 6 points
#     preview = []
#     vals = st.session_state.anomaly_cache["values"]
#     tss = st.session_state.anomaly_cache["ts"]
#     for i in range(max(0, len(vals) - 6), len(vals)):
#         preview.append({"ts": tss[i] if i < len(tss) else "", "value": vals[i]})
#     st.json(preview)
