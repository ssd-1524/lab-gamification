from __future__ import annotations

from typing import Any, Dict
import requests
import streamlit as st

from utils.sessions import get_access_token, is_authenticated
from utils.events import log_event
import streamlit.components.v1 as components

# ------------------ Guards ------------------ #

if not is_authenticated():
    st.switch_page("pages/auth.py")

# 🔴 PAGE VIEW EVENT
log_event("profile", "page_view")

API_BASE_URL = "http://localhost:8000"
# ------------------ Fetch Profile Data ------------------ #

def fetch_profile() -> Dict[str, Any]:
    """
    Fetch profile data from backend.
    """

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
log_event(
    "wallet",
    "view",
    {"total_points": wallet["total_points"]},
)

st.metric("Rank", wallet["rank"])
log_event(
    "wallet",
    "rank_view",
    {"rank": wallet["rank"]},
)

st.markdown(
    """
    <style>
    .badge-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 20px;
        margin-top: 10px;
    }

    .badge-card {
        perspective: 1000px;
        height: 200px;
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
        width: 100%;
        height: 100%;
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
        background-color: white;
    }


    .badge-back {
        transform: rotateY(180deg);
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: white;
        font-weight: 600;
        font-size: 16px;
        text-align: center;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 20px;
        margin-top: 10px;
    }
 
    .badge-card {
        perspective: 1000px;
        height: 170px;
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
        width: 100%;
        height: 100%;
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
        color: black;
        font-weight: 300;
        font-size: 25px;
        font-family: 'Source Sans Pro', sans-serif;
        text-align: center;
        padding: 12px;
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
                     style="background-image:url('{image_url}')">
</div>
<div class="badge-face badge-back">
                    {badge_name}
</div>
</div>
</div>
        """
 
    html += "</div>"
 
    components.html(html, height=450, scrolling=True)