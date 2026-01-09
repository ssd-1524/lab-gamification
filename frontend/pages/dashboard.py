from __future__ import annotations
import streamlit as st
import time
import requests
from datetime import datetime
from pytz import timezone
from textwrap import dedent

from utils.api_client import get_user_points
from utils.events import log_event
from utils.sessions import get_access_token
from utils.api_client import get_plant_state
from utils.ui_utils import FEATURE_GUIDES
from utils.theme import apply_theme


API_BASE_URL = "https://lab-gamification.onrender.com"

st.set_page_config(page_title="Dashboard - Stomata Labs", page_icon="📊", layout="wide")
IST = timezone("Asia/Kolkata")
apply_theme()

# ---------------- Security ---------------- #
if not st.session_state.get("is_authenticated"):
    st.warning("Please login to access the dashboard.")
    st.switch_page("streamlit_app.py")
    st.stop()

log_event("dashboard", "page_view")

user = st.session_state.user
points_data = get_user_points()

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ---------------- Quiz Status ---------------- #
quiz_resp = requests.get(f"{API_BASE_URL}/quizzes/status", headers=headers)
quiz_completed = quiz_resp.json().get("completed", False) if quiz_resp.status_code == 200 else False

# ---------------- Streak ---------------- #
streak_resp = requests.get(f"{API_BASE_URL}/sessions/streak", headers=headers)
streak = streak_resp.json().get("streak", 0) if streak_resp.status_code == 200 else 0

# ---------------- Rank ---------------- #
rank_resp = requests.get(f"{API_BASE_URL}/users/me/rank", headers=headers)
rank_data = rank_resp.json() if rank_resp.status_code == 200 else {}

# ---------------- Header ---------------- #
st.markdown("## 👋 Welcome back")
st.markdown(f"### **{user['name']}**")

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("📍 **Location**")
        st.markdown(user.get("loc_name", "—"))

    with col2:
        st.markdown("🛠️ **Role**")
        st.markdown(user.get("role_name", "—"))

st.divider()


st.markdown(
    dedent(
        """
    <style>
    /* baseline card */
    .metric-card {
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(12,14,20,0.04);
        border: 1px solid rgba(15,23,42,0.06);
        background: #ffffff;
        height:100%;
        box-sizing:border-box;
    }

    /* black & white card for points */
    .bw-card {
        background: #0b0b0b !important;
        color: #ffffff !important;
    }
    .bw-card .muted {
        color: rgba(255,255,255,0.75) !important;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.6px;
    }
    .bw-card .big-value {
        font-size: 40px;
        font-weight: 800;
        line-height: 1;
        color: #ffffff;
    }
    .bw-card .small-value {
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
    }

    /* tier card specifics */
    .tier-card .title {
        font-size: 13px;
        color: #6b7280;
        font-weight: 700;
        letter-spacing: 0.6px;
    }
    .tier-card .tier-name {
        font-size: 20px;
        color: #0f172a;
        font-weight: 800;
        margin-top: 6px;
    }
    .tier-card .tier-body {
        display:flex;
        gap:12px;
        align-items:center;
        margin-top:12px;
    }
    .tier-card img.badge {
        height:56px;
        width:auto;
        border-radius:8px;
        object-fit:contain;
    }

    /* ensure equal heights */
    .card-outer { height: 100%; }

    @media (max-width: 640px) {
        /* stack on small screens */
        .card-row { flex-direction: column !important; gap: 12px !important; }
    }
    </style>
    """
    ),
    unsafe_allow_html=True,
)

# columns: left is wider (points+rank), right is for tier card
col_left, col_right = st.columns([2, 1], gap="large")

# -------- LEFT: Points + Rank (B&W styled card) --------
with col_left:
    total_points = int(rank_data.get("points", 0) or 0)
    position = rank_data.get("position") or "—"

    points_html = dedent(
        f"""
    <div class="metric-card bw-card card-outer" role="region" aria-label="points-card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div class="muted">POINTS</div>
          <div class="big-value">{total_points:,}</div>
        </div>
        <div style="text-align:right;">
          <div class="muted">RANK</div>
          <div class="small-value">{position}</div>
        </div>
      </div>

      <div style="margin-top:14px;display:flex;justify-content:space-between;align-items:center;">
        <div style="flex:1;color:rgba(255,255,255,0.88);font-size:13px;">
          Keep your streak — complete daily training to earn more points.
        </div>
        <div>
          <!-- Visual CTA (non-interactive) — keep interactions via Streamlit buttons if required -->
          <div style="display:inline-block;padding:8px 14px;border-radius:8px;background:transparent;border:1px solid rgba(255,255,255,0.12);color:white;font-weight:700;">
            View Wallet
          </div>
        </div>
      </div>
    </div>
    """
    )
    st.markdown(points_html, unsafe_allow_html=True)
    # record wallet view impression
    try:
        log_event("wallet", "view")
    except Exception:
        pass

# -------- RIGHT: Tier + Badge (white card) --------
with col_right:
    tier_name = rank_data.get("rank") or "—"
    badge_image = rank_data.get("badge_image")  # may be None

    tier_html = dedent(
        f"""
    <div class="metric-card tier-card card-outer" role="region" aria-label="tier-card">
      <div class="title">CURRENT TIER</div>
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <div style="flex:1;">
          <div class="tier-name">{tier_name}</div>
          <div style="font-size:13px;color:#475569;margin-top:8px;font-weight:600;">Membership</div>
        </div>
      </div>
      <div class="tier-body">
    """
    )

    if badge_image:
        # include badge image inside the card
        tier_html += dedent(f"""<img class="badge" src="{badge_image}" alt="badge" />""")
    else:
        tier_html += dedent(
            """<div style="width:56px;height:56px;border-radius:8px;background:#f3f4f6;display:flex;align-items:center;justify-content:center;">
                 <div style="font-weight:700;color:#9ca3af;">—</div>
               </div>"""
        )

    tier_html += "</div></div>"

    st.markdown(tier_html, unsafe_allow_html=True)

st.divider()

# ---------------- Plant Growth Gamification ---------------- #
with st.container(border=True):
    st.markdown("## 🌱 Your Growth Journey")

    plant_state = get_plant_state()

    if plant_state:
        col_img, col_text = st.columns([2, 3], vertical_alignment="center")

        # -------- Plant Image --------
        with col_img:
            st.image(
                plant_state["image_url"],
                width=280,
            )

        # -------- Text Content --------
        with col_text:
            st.markdown(f"### {plant_state['message']}")
            st.markdown(f"#### 🔥 Login Streak: **{plant_state['streak']} days**")

            st.markdown("<br>", unsafe_allow_html=True)

            if plant_state.get("can_replant"):
                if st.button("🌱 Plant seed again", type="secondary"):
                    # 🔥 log real replant event
                    log_event("plant", "replanted")

                    # 🔁 refresh backend-derived plant state
                    st.session_state["_force_plant_refresh"] = datetime.now(IST).isoformat()

                    st.success("A new seed has been planted 🌱 Come back tomorrow!")
                    st.rerun()
    else:
        st.info("🌱 Your plant will appear once you start your journey!")

st.divider()


# ---------------- Guides ---------------- #
st.subheader("📖 Feature Guides")

cols = st.columns(len(FEATURE_GUIDES))

for idx, (key, data) in enumerate(FEATURE_GUIDES.items()):
    with cols[idx]:

        if st.button(
            f"🎯 {data['title']}\n\n{data['subtitle']}",
            key=f"guide_btn_{key}",
            use_container_width=True
        ):
            log_event("guides", "open_from_dashboard", {"guide": key})
            st.session_state.selected_guide = key
            st.switch_page("pages/guides.py")

st.divider()



# ---------------- Quiz Popup / Timer ---------------- #
if quiz_completed:
    st.subheader("⏳ Next Quiz Available In")

    resp = requests.get(f"{API_BASE_URL}/quizzes/next-available", headers=headers)
    if resp.status_code == 200:
        remaining = resp.json()["seconds_remaining"]
        timer = st.empty()

        while remaining > 0:
            h, r = divmod(remaining, 3600)
            m, s = divmod(r, 60)
            timer.metric("Next Daily Quiz", f"{h:02d}:{m:02d}:{s:02d}")
            time.sleep(1)
            remaining -= 1
else:
    with st.container(border=True):
        st.markdown("### 🎯 Daily Training Available")
        st.write(f"Hello **{user['name']}**! Ready to earn points today?")
        col1, col2 = st.columns([1, 4])

        with col1:
            if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
                log_event("dashboard", "start_quiz_click")
                st.switch_page("pages/quizzes.py")

        with col2:
            if st.button("🕒 Maybe Later", use_container_width=True):
                log_event("dashboard", "maybe_later_click")
                st.rerun()

st.divider()
