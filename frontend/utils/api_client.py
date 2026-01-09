import requests
from utils.sessions import get_access_token
from utils.config_loader import load_config
import streamlit as st

config = load_config()

API_BASE_URL = "https://lab-gamification.onrender.com"
SUPABASE_URL = config["SUPABASE_URL"]
SUPABASE_ANON_KEY = config["SUPABASE_ANON_KEY"]

def get_roles():
    try:
        r = requests.get(f"{API_BASE_URL}/roles/", timeout=50)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print("get_roles:", e)
        return []


def get_locations():
    try:
        r = requests.get(f"{API_BASE_URL}/locations/", timeout=50)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print("get_locations:", e)
        return []


def signup_user(payload: dict):
    try:
        r = requests.post(f"{API_BASE_URL}/auth/signup", json=payload, timeout=50)
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def login_user(payload: dict):
    try:
        r = requests.post(f"{API_BASE_URL}/auth/login", json=payload, timeout=50)
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def get_user_points():
    token = get_access_token()
    if not token:
        return {"total_points": 0, "rank": None}

    try:
        r = requests.get(
            f"{API_BASE_URL}/profile/me/rank",
            headers={"Authorization": f"Bearer {token}"},
            timeout=50,
        )
        return r.json() if r.status_code == 200 else {"total_points": 0, "rank": None}
    except Exception as e:
        print("get_user_points:", e)
        return {"total_points": 0, "rank": None}


def get_plant_state():
    token = get_access_token()
    if not token:
        return None

    # 🔁 Bust Streamlit request caching when plant state changes
    refresh_token = st.session_state.get("_force_plant_refresh", "")

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Refresh": refresh_token,
    }

    try:
        response = requests.get(
            f"{API_BASE_URL}/profile/plant-state",
            headers=headers,
            timeout=10,
        )
    except Exception:
        return None

    if response.status_code != 200:
        return None

    return response.json()

