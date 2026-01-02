from __future__ import annotations

from typing import Any, Dict, Generator

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import get_settings

# ------------------ Configuration ------------------ #
settings = get_settings()
security = HTTPBearer(auto_error=True)

# Supabase JWKS URL for RS256 verification
JWKS_URL = f"{settings.SUPABASE_URL}/auth/v1/keys"

# ------------------ Database Dependency ------------------ #

def get_db() -> Generator[Session, None, None]:
    """
    Creates a new SQLAlchemy session for a request and ensures 
    it is closed once the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Auth Dependencies ------------------ #

async def _get_jwks() -> Dict[str, Any]:
    """Fetches public keys from Supabase to verify JWT signatures locally."""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(JWKS_URL)
        response.raise_for_status()
        return response.json()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Decodes and validates the Supabase RS256 JWT.
    Returns the decoded token payload (claims) if valid.
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
            headers={"WWW-Authenticate": "Bearer"},
        )