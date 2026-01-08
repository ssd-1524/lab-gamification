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

API_BASE_URL = "https://lab-gamification.onrender.com"

# ------------------ Fetch Profile Data ------------------ #

def fetch_profile() -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    response = requests.get(
        f"{API_BASE_URL}/profile/me/details",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


profile = fetch_profile()
user = profile["user"]

# ------------------ UI ------------------ #

st.title(f"👤 {user['name']}")

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

        .badge-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            width: 100%;
            margin-top: 10px;
            padding-bottom: 200px;
            border-radius: 16px;
        }

        .badge-card {
            perspective: 1000px;
            width: 100%;
            aspect-ratio: 1 / 1;
            padding-bottom: 20px;
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

        log_event("badge", "view", {"badge_name": badge_name})

    html += "</div>"

    # 🔥 DYNAMIC HEIGHT CALCULATION (KEY FIX)
    badges_per_row = 4
    rows = (len(badges) + badges_per_row - 1) // badges_per_row
    iframe_height = rows * 270  # ~220px per row

    components.html(
        html,
        height=iframe_height,
        scrolling=False,
    )



points_history = profile.get("points_history", [])

if not points_history:
    st.info("No points history available yet.")
else:
    history_html = """
    <style>
        .points-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            padding: 16px;
            margin-top: 10px;
        }

        .points-title {
            font-weight: 600;
            font-size: 18px;
            font-family: 'Source Sans Pro', sans-serif;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .points-table {
            width: 100%;
            border-collapse: collapse;
        }

        .points-table thead {
            background-color: #f9fafb;
        }

        .points-table th {
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            font-family: 'Source Sans Pro', sans-serif;
            color: #374151;
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
        }

        .points-table td {
            padding: 12px 10px;
            font-size: 14px;
            font-family: 'Source Sans Pro', sans-serif;
            border-bottom: 1px solid #f1f5f9;
        }

        .points-table tbody tr:hover {
            background-color: #f9fafb;
        }

        .points-value {
            font-weight: 600;
            color: #111827;
            width: 90px;
        }

        .points-reason {
            color: #111827;
        }

        .points-date {
            color: #6b7280;
            text-align: right;
            white-space: nowrap;
        }

        .table-wrapper {
            max-height: 280px; /* scroll if long */
            overflow-y: auto;
        }
    </style>

    <div class="points-card">
        <div class="points-title">🪙 Points History</div>

        <div class="table-wrapper">
            <table class="points-table">
                <thead>
                    <tr>
                        <th>Points</th>
                        <th>Reason</th>
                        <th style="text-align:right;">Date</th>
                    </tr>
                </thead>
                <tbody>
    """

    for row in points_history:
        history_html += f"""
        <tr>
            <td class="points-value">+{row["points"]}</td>
            <td class="points-reason">{row["reason"]}</td>
            <td class="points-date">{row["date"]}</td>
        </tr>
        """

        # 🔴 Optional event tracking
        log_event(
            "points_history",
            "row_view",
            {"reason": row["reason"], "points": row["points"]},
        )

    history_html += """
                </tbody>
            </table>
        </div>
    </div>
    """

    components.html(history_html, height=360, scrolling=False)
