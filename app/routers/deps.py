from __future__ import annotations

from typing import Any, Dict, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.database import SessionLocal

security = HTTPBearer(auto_error=True)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    print("🔥 AUTH DEPENDENCY HIT")

    token = credentials.credentials

    try:
        payload = jwt.get_unverified_claims(token)

        return {
            "sub": payload["sub"],
            "email": payload.get("email"),
            "role": payload.get("role"),
        }

    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
