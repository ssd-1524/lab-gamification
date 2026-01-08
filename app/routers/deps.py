from __future__ import annotations

from typing import Any, Dict, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_session_local
from app.models.schema import Users as User, Sessions as UserSession, Location

security = HTTPBearer(auto_error=True)

SessionLocal = get_session_local()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Decode Supabase JWT WITHOUT verification and resolve DB identity context.
    """

    token = credentials.credentials

    try:
        payload = jwt.get_unverified_claims(token)

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token: subject missing")

        user_id = UUID(sub)

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not registered")


        # 2. Fetch active session
        session = (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user.user_id,
                UserSession.logout_time.is_(None)
            )
            .order_by(UserSession.login_time.desc())
            .first()
        )

        if not session:
            raise HTTPException(status_code=401, detail="No active session")

        # 3. Resolve plan via location
        location = db.query(Location).filter(Location.loc_id == user.loc_id).first()
        if not location:
            raise HTTPException(status_code=401, detail="Location not found")

        return {
            "user_id": user.user_id,
            "session_id": session.session_id,
            "plan_id": location.plan_id,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
