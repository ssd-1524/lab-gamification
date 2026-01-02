from __future__ import annotations

from typing import Any, Dict
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from supabase import create_client, Client

# Import the settings loader
from app.config import get_settings

# 1. Load settings once
settings = get_settings()

# 2. Use settings object instead of os.getenv
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY

# This check is now redundant if Pydantic has already validated them, 
# but we can keep it for safety.
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are missing from config.")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/keys"
security = HTTPBearer(auto_error=True)

# ------------------ Admin Client ------------------ #
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ------------------ JWT Verification ------------------ #

async def _get_jwks() -> Dict[str, Any]:
    """Fetch public keys from Supabase to verify RS256 signatures locally."""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(JWKS_URL)
        response.raise_for_status()
        return response.json()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Validates the Supabase RS256 JWT.
    Used for protected routes (e.g., /quizzes/today).
    """
    token = credentials.credentials

    try:
        jwks = await _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience="authenticated",
            options={"verify_aud": False},
        )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )