from __future__ import annotations

import requests
import streamlit as st
from utils.sessions import is_authenticated, get_access_token
from utils.events import log_event

API_BASE = "http://localhost:8000"

# ---------------- Guards ---------------- #
if not is_authenticated():
    st.switch_page("pages/auth.py")

st.set_page_config(page_title="Optimizer", layout="wide")

log_event("optimizer", "page_view")

st.title("⚙️ Process Optimizer")

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Fetch Stream ---------------- #
resp = requests.get(f"{API_BASE}/optimizer/stream", headers=headers)

if resp.status_code != 200:
    st.error("Unable to load optimizer stream.")
    st.stop()

data = resp.json()

eff = [d["efficiency"] for d in data]
cost = [d["cost"] for d in data]

st.subheader("Efficiency Trend (%)")
st.line_chart({"Efficiency": eff})

st.subheader("Energy Cost (₹/hr)")
st.line_chart({"Cost": cost})

# ---------------- Mock Recommendation ---------------- #
improvement = 6  # mock %
points = int(improvement * 2)

st.subheader("💡 Recommendation")
st.write(f"Applying suggested optimization can improve efficiency by **{improvement}%**.")

col1, col2 = st.columns(2)

with col1:
    if st.button(f"Apply Optimization (+{points} pts)"):
        log_event("optimizer", "accept", {"improvement": improvement})

        requests.post(
            f"{API_BASE}/bonus/reward",
            headers=headers,
            json={
                "feature": "optimizer",
                "points": points,
                "metadata": {"improvement": improvement},
            },
        )
        st.success(f"Bonus +{points} points awarded!")

with col2:
    if st.button("Reject"):
        log_event("optimizer", "reject", {"improvement": improvement})
        st.info("Optimization rejected.")
