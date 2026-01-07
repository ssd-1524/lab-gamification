from __future__ import annotations

from typing import Any, Dict
import requests
import streamlit as st
import streamlit.components.v1 as components

from utils.sessions import get_access_token, is_authenticated
from utils.events import log_event

# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")

# 🔴 PAGE VIEW EVENT
log_event("profile", "page_view")

API_BASE_URL = "http://localhost:8000"

# ------------------ Fetch Profile Data ------------------ #

def fetch_profile() -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    response = requests.get(
        f"{API_BASE_URL}/profile/me",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


profile = fetch_profile()
user = profile["user"]

# ------------------ UI ------------------ #

st.title("👤 My Profile")
st.write(f"**Name:** {user.get('name', 'User')}")

# ------------------ Wallet ------------------ #

wallet = profile["wallet"]

st.markdown("### 🪙 Points Wallet")
st.metric("Total Points", wallet["total_points"])
log_event("wallet", "view", {"total_points": wallet["total_points"]})

st.metric("Rank", wallet["rank"])
log_event("wallet", "rank_view", {"rank": wallet["rank"]})

# ------------------ Badges ------------------ #

st.markdown("### 🏅 Badges Earned")

badges = profile.get("badges", [])

if not badges:
    st.info("No badges earned yet.")
else:
    html = """
    <style>
        * {
            box-sizing: border-box;
        }

        /* ===== BADGE MATRIX ===== */
        .badge-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr); /* MAX 4 COLUMNS */
            gap: 20px;
            width: 100%;
            margin-top: 10px;
        }

        .badge-card {
            perspective: 1000px;
            width: 100%;
            aspect-ratio: 1 / 1; /* Keeps cards square */
        }

        .badge-card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.6s;
            transform-style: preserve-3d;
        }

        .badge-card:hover .badge-card-inner {
            transform: rotateY(180deg);
        }

        .badge-face {
            position: absolute;
            inset: 0;
            overflow: hidden;
            backface-visibility: hidden;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: white;
        }

        .badge-front {
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }

        .badge-back {
            transform: rotateY(180deg);
            color: #111;
            font-weight: 500;
            font-size: 18px;
            text-align: center;
            padding: 12px;
            line-height: 1.2;
            font-family: 'Source Sans Pro', sans-serif;
        }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 900px) {
            .badge-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }

        @media (max-width: 600px) {
            .badge-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 400px) {
            .badge-grid {
                grid-template-columns: repeat(1, 1fr);
            }
        }
    </style>

    <div class="badge-grid">
    """

    for badge in badges:
        image_url = (
            badge["images"][0]
            if isinstance(badge.get("images"), list)
            else badge.get("images")
        )
        badge_name = badge.get("name", "Badge")

        html += f"""
        <div class="badge-card">
            <div class="badge-card-inner">
                <div class="badge-face badge-front"
                     style="background-image: url('{image_url}');">
                </div>
                <div class="badge-face badge-back">
                    {badge_name}
                </div>
            </div>
        </div>
        """

        # 🔴 Badge view event
        log_event("badge", "view", {"badge_name": badge_name})

    html += "</div>"

    components.html(html, height=500, scrolling=False)
