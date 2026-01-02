import requests

API_BASE_URL = "http://localhost:8000"

def get_roles():
    """Fetches all roles from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/roles/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching roles: {e}")
        return []

def get_locations():
    """Fetches all locations from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/locations/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return []

def signup_user(payload: dict):
    """Sends signup data to the backend."""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/signup/", json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def login_user(payload: dict):
    """Sends login credentials to the backend."""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login/", json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def get_user_points(user_id: str):
    """Fetches the point wallet for a specific user."""
    try:
        # Note: Ensure your backend has this route implemented
        response = requests.get(f"{API_BASE_URL}/auth/points/{user_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"total_points": 0, "rank": "Bronze"}
    except Exception as e:
        print(f"Error fetching points: {e}")
        return {"total_points": 0, "rank": "Bronze"}
    
def log_event(token: str, payload: dict) -> bool:
    """
    Sends a gamification / analytics event to backend
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{API_BASE_URL}/events/",
            json=payload,
            headers=headers,
            timeout=5,
        )

        return response.status_code == 200

    except Exception as e:
        print(f"Error logging event: {e}")
        return False
