import requests
from utils.sessions import get_access_token

API_BASE_URL = "http://localhost:8000"


def get_roles():
    try:
        r = requests.get(f"{API_BASE_URL}/roles/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print("get_roles:", e)
        return []


def get_locations():
    try:
        r = requests.get(f"{API_BASE_URL}/locations/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print("get_locations:", e)
        return []


def signup_user(payload: dict):
    try:
        r = requests.post(f"{API_BASE_URL}/auth/signup/", json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def login_user(payload: dict):
    try:
        r = requests.post(f"{API_BASE_URL}/auth/login/", json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def get_user_points():
    token = get_access_token()
    if not token:
        return {"total_points": 0, "rank": None}

    try:
        r = requests.get(
            f"{API_BASE_URL}/auth/points",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        return r.json() if r.status_code == 200 else {"total_points": 0, "rank": None}
    except Exception as e:
        print("get_user_points:", e)
        return {"total_points": 0, "rank": None}

def get_plant_state():
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{API_BASE_URL}/profile/plant-state",
        headers=headers,
        timeout=10
    )

    if response.status_code != 200:
        return None

    return response.json()

