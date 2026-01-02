from __future__ import annotations

from typing import Any, Dict, List

import requests

from utils.api_client import _auth_headers, _handle_response  # type: ignore


# ---------------------- Analytics ---------------------- #


def get_leaderboard(token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        "http://localhost:8000/analytics/leaderboard",
        headers=_auth_headers(token),
        timeout=10,
    )
    return _handle_response(response)


def get_usage_metrics(token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        "http://localhost:8000/analytics/usage",
        headers=_auth_headers(token),
        timeout=10,
    )
    return _handle_response(response)
