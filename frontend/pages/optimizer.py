from __future__ import annotations

import requests
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
from typing import List, Dict, Any, Optional

from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event
from utils.theme import apply_theme

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "https://lab-gamification.onrender.com"

# === Page config ===
st.set_page_config(page_title="Optimizer", layout="wide")
apply_theme()
# === Guards ===
if not is_authenticated():
    st.switch_page("pages/auth.py")

# === Session state defaults ===
st.session_state.setdefault("optimizer_page_view_logged", False)
st.session_state.setdefault("optimizer_cache", {"ts": [], "eff": [], "cost": [], "throughput": []})
st.session_state.setdefault("last_fetch_ok", False)
st.session_state.setdefault("last_fetch_time", None)
st.session_state.setdefault("opt_suggestion_active", False)
st.session_state.setdefault("opt_suggestion_start_ts", None)
st.session_state.setdefault("opt_suggestion_key", None)
st.session_state.setdefault("opt_suggestion_payload", None)  # store the suggestion dict

# === Auto-refresh ===
REFRESH_INTERVAL_MS = 10_000  # 10s
# pause auto-refresh while a suggestion is active so button clicks aren't lost
if not st.session_state.opt_suggestion_active:
    st_autorefresh(interval=REFRESH_INTERVAL_MS, key="optimizer_autorefresh")

# === Page view event (once) ===
if not st.session_state.optimizer_page_view_logged:
    try:
        log_event("optimizer", "page_view")
    except Exception:
        pass
    st.session_state.optimizer_page_view_logged = True

st.title("⚙️ Optimizer – Live KPIs")

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

fetch_error: Optional[str] = None

# === Fetch stream (best-effort; update cache only on success) ===
try:
    resp = requests.get(f"{API_BASE}/optimizer/stream", headers=headers, timeout=4)
    if resp.status_code == 403:
        st.error("Optimizer is available for Nexus plan only. Upgrade to access this feature.")
        st.stop()
    elif resp.status_code != 200:
        fetch_error = f"Stream fetch failed: HTTP {resp.status_code}"
    else:
        payload = resp.json()
        effs: List[int] = []
        costs: List[int] = []
        tputs: List[int] = []
        tss: List[str] = []
        suggestion_obj = None

        for item in payload:
            try:
                tss.append(item.get("ts"))
                effs.append(int(item.get("efficiency", 0)))
                costs.append(int(item.get("cost", 0)))
                tputs.append(int(item.get("throughput", 0)))
                # suggestion only matters for the latest point; capture if present
                if item.get("suggestion") and item["suggestion"].get("suggested"):
                    suggestion_obj = item["suggestion"]
            except Exception:
                continue

        if effs:
            st.session_state.optimizer_cache = {
                "ts": tss,
                "eff": effs,
                "cost": costs,
                "throughput": tputs,
            }
            st.session_state.last_fetch_ok = True
            st.session_state.last_fetch_time = datetime.now(IST).isoformat()

            # Persist suggestion across reruns (important)
            if suggestion_obj:
                # set start timestamp only once per suggestion activation
                if not st.session_state.opt_suggestion_active:
                    st.session_state.opt_suggestion_start_ts = datetime.now(IST)
                    st.session_state.opt_suggestion_key = int(st.session_state.opt_suggestion_start_ts.timestamp())
                # keep suggestion active and persist payload so reruns don't lose it
                st.session_state.opt_suggestion_active = True
                st.session_state.opt_suggestion_payload = suggestion_obj

                # log suggestion event (once) — best-effort
                # we keep this as fire-and-forget; it's non-critical telemetry
                try:
                    log_event("optimizer", "suggested", {"suggestion": suggestion_obj})
                except Exception:
                    pass

except requests.RequestException as e:
    fetch_error = f"Stream request error: {e}"

# === Use cached data to always render charts ===
cache = st.session_state.optimizer_cache
if not cache["eff"]:
    st.warning("No optimizer data available yet — waiting for first successful fetch.")
    if fetch_error:
        st.info(fetch_error)
    st.stop()

# Build DataFrame
df = pd.DataFrame({
    "ts": cache["ts"],
    "efficiency": cache["eff"],
    "cost": cache["cost"],
    "throughput": cache["throughput"],
})

try:
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts")
except Exception:
    pass

# === Charts ===
st.subheader("KPIs (last 24 hours)")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.line_chart(df[["efficiency"]])
    st.line_chart(df[["cost"]])
    st.line_chart(df[["throughput"]])

with col_right:
    st.metric("Last fetch", st.session_state.last_fetch_time or "N/A")
    if st.session_state.last_fetch_ok:
        st.success("Live")
    else:
        st.warning("Offline")

# === Optimization suggestion UI ===
if st.session_state.opt_suggestion_active and st.session_state.opt_suggestion_payload:
    suggestion = st.session_state.opt_suggestion_payload
    severity = suggestion.get("severity", "Medium")
    est_gain = suggestion.get("estimated_efficiency_gain_pct", 0)
    points = int(suggestion.get("suggested_points", 0))

    st.divider()
    st.subheader("🔧 Optimization Suggestion")
    st.write(
        f"Estimated efficiency gain: **{est_gain}%**.\n\n"
    )

    event_key = st.session_state.opt_suggestion_key or int(datetime.now(IST).timestamp())
    accept_key = f"opt_accept_{event_key}"
    ignore_key = f"opt_ignore_{event_key}"

    c1, c2 = st.columns(2)

    with c1:
        if st.button(f"Apply Optimization (+{points} pts)", key=accept_key):
            resolved_at = datetime.now(IST)
            detected_at = st.session_state.opt_suggestion_start_ts

            if detected_at:
                response_time = round((resolved_at - detected_at).total_seconds(), 2)
            else:
                response_time = 99999

            # Synchronous guaranteed event POST (critical action)
            try:
                if token:
                    requests.post(
                        f"{API_BASE}/events/",
                        headers=headers,
                        json={
                            "feature": "optimizer",
                            "action": "accepted",
                            "metadata": {"suggestion": suggestion, "response_time_sec": response_time},
                        },
                        timeout=3,
                    )
            except Exception:
                # show a small message so you know if event logging failed
                st.error("Failed to log optimization acceptance to server.")

            # best-effort call to award bonus (as before)
            try:
                if token:
                    requests.post(
                        f"{API_BASE}/bonus/reward",
                        headers=headers,
                        json={
                            "feature": "optimizer",
                            "points": points,
                            "metadata": {"suggestion": suggestion, "response_time_sec": response_time},
                        },
                        timeout=3,
                    )
            except Exception:
                st.warning("Bonus call failed (best-effort).")

            # clear suggestion state
            st.session_state.opt_suggestion_active = False
            st.session_state.opt_suggestion_start_ts = None
            st.session_state.opt_suggestion_key = None
            st.session_state.opt_suggestion_payload = None

            st.success(f"Optimization applied — Bonus +{points} pts awarded!")

    with c2:
        if st.button("Ignore Suggestion", key=ignore_key):
            # Synchronous ignored event logging
            try:
                if token:
                    requests.post(
                        f"{API_BASE}/events/",
                        headers=headers,
                        json={
                            "feature": "optimizer",
                            "action": "ignored",
                            "metadata": {"suggestion": suggestion},
                        },
                        timeout=3,
                    )
            except Exception:
                st.error("Failed to log ignore action to server.")

            st.session_state.opt_suggestion_active = False
            st.session_state.opt_suggestion_start_ts = None
            st.session_state.opt_suggestion_key = None
            st.session_state.opt_suggestion_payload = None

            st.info("Suggestion ignored.")

# # === Optional debug expander ===
# with st.expander("Optimizer debug", expanded=False):
#     st.write("Last fetch OK:", st.session_state.last_fetch_ok)
#     st.write("Last fetch time:", st.session_state.last_fetch_time)
#     if fetch_error:
#         st.write("Fetch error:", fetch_error)
#     st.json({
#         "cached_points": len(cache["eff"]),
#         "suggestion_active": st.session_state.opt_suggestion_active,
#         "suggestion_payload": st.session_state.opt_suggestion_payload,
#     })
