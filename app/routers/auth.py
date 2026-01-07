# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from uuid import UUID, uuid4
from datetime import datetime
import pytz
import logging
from typing import Optional

from app.routers.deps import get_db, get_authenticated_user
from app.models import schema
from app.utils.auth import supabase
from pydantic import BaseModel, EmailStr

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/auth", tags=["Authentication"])

logger = logging.getLogger(__name__)


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: UUID
    loc_id: UUID


class UserLogin(BaseModel):
    email: EmailStr
    password: str


def _get_existing_auth_user_by_email(email: str) -> Optional[str]:
    """
    Try several supabase admin methods to fetch an existing auth user by email.
    Return the user id string if found, else None.

    Note: supabase admin API methods differ across client versions; try multiple shapes.
    """
    try:
        # preferred: admin API exposing a helper to get user by email (if available)
        if hasattr(supabase.auth, "admin") and hasattr(supabase.auth.admin, "get_user_by_email"):
            u = supabase.auth.admin.get_user_by_email(email)
            # u may be an object or dict
            if not u:
                return None
            if hasattr(u, "id"):
                return u.id
            if isinstance(u, dict) and u.get("id"):
                return u.get("id")
    except Exception as ex:
        logger.debug("get_user_by_email not available or failed: %s", ex)

    try:
        # another possible shape in different clients
        if hasattr(supabase.auth, "admin") and hasattr(supabase.auth.admin, "list_users"):
            # list_users may accept filters in some versions; fallback to scanning
            users = supabase.auth.admin.list_users()  # may return dict/object with 'users' list
            if users is None:
                return None
            if isinstance(users, dict) and users.get("users"):
                for u in users["users"]:
                    if u.get("email") == email:
                        return u.get("id")
            # object style
            if hasattr(users, "data") and isinstance(getattr(users, "data"), list):
                for u in users.data:
                    if u.get("email") == email:
                        return u.get("id")
    except Exception as ex:
        logger.debug("list_users not available or failed: %s", ex)

    try:
        # legacy supabase client shape: supabase.auth.api.get_user_by_email
        if hasattr(supabase.auth, "api") and hasattr(supabase.auth.api, "get_user_by_email"):
            u = supabase.auth.api.get_user_by_email(email)
            if not u:
                return None
            if isinstance(u, dict) and u.get("id"):
                return u.get("id")
            if hasattr(u, "id"):
                return u.id
    except Exception as ex:
        logger.debug("auth.api.get_user_by_email not available or failed: %s", ex)

    return None


@router.post("/signup")
async def signup(payload: UserSignup, db: Session = Depends(get_db)):
    """
    Robust signup:
    - Validate role_id and loc_id first (prevent creating an auth-only user when payload invalid).
    - Attempt supabase.auth.sign_up. If 'User already registered', try to link the existing auth user:
       * fetch auth user id from admin APIs
       * if local users row exists -> return "already registered"
       * else create local users + pointwallet for that auth id
    - On new auth user creation, create local users + pointwallet after db.flush() to avoid FK races.
    - Clean up (delete) Supabase auth user only when we created it in this request and subsequent DB work fails.
    """
    created_auth_user_id: Optional[str] = None
    try:
        # Validate role & location up-front
        role = db.query(schema.Role).filter(schema.Role.role_id == payload.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role_id supplied")

        loc = db.query(schema.Location).filter(schema.Location.loc_id == payload.loc_id).first()
        if not loc:
            raise HTTPException(status_code=400, detail="Invalid loc_id supplied")

        # Attempt to create auth user
        try:
            auth_res = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
            # auth_res may be an object with .user or a dict
            user_obj = getattr(auth_res, "user", None) or (auth_res.get("user") if isinstance(auth_res, dict) else None)
            if not user_obj:
                # If we don't get a created user back, attempt to detect existing user error via response shape
                # Fall through to exception handling below
                raise Exception("Auth provider did not return created user object")
            created_auth_user_id = getattr(user_obj, "id", None) or (user_obj.get("id") if isinstance(user_obj, dict) else None)
            if not created_auth_user_id:
                raise Exception("Auth provider returned unexpected user shape")
            auth_user_id = created_auth_user_id
            user_id = UUID(auth_user_id)

        except Exception as auth_exc:
            # If Supabase says "User already registered", try to link existing auth user
            msg = str(auth_exc)
            logger.debug("Supabase sign_up exception: %s", msg)

            if "User already registered" in msg or "already registered" in msg.lower() or "user already" in msg.lower():
                # find the existing auth user id via admin/helper endpoints
                found_id = _get_existing_auth_user_by_email(payload.email)
                if not found_id:
                    # We couldn't find their auth record programmatically, return helpful message
                    raise HTTPException(status_code=400, detail="Email already registered with auth provider; please login or contact admin.")

                logger.info("Email %s already registered in auth provider as user %s. Attempting to link local user.", payload.email, found_id)
                auth_user_id = found_id
                user_id = UUID(auth_user_id)

                # check if local user row already exists:
                existing_local = db.query(schema.Users).filter(schema.Users.user_id == user_id).first()
                if existing_local:
                    # The user exists both in auth provider and locally: normal "already registered"
                    raise HTTPException(status_code=400, detail="User already registered. Please login.")
                # else: we'll proceed to create local user + wallet for this existing auth user
            else:
                # unexpected auth error: return as 400 with message
                # If auth_exc contains an object with details, include carefully
                raise HTTPException(status_code=400, detail=f"Auth provider error: {msg}")

        # At this point we have `user_id` (UUID) for either newly created auth user or an existing auth user we found.
        # Create local Users row, flush to ensure DB visibility before wallet insert.
        new_user = schema.Users(
            user_id=user_id,
            name=payload.name,
            role_id=payload.role_id,
            loc_id=payload.loc_id,
        )
        db.add(new_user)
        db.flush()  # ensure users row exists for FK checks

        # Create PointWallet row
        wallet = schema.PointWallet(user_id=user_id, total_points=0, rank="Bronze")
        db.add(wallet)

        db.commit()

        return {"status": "success"}

    except HTTPException:
        # re-raise controlled HTTP errors
        raise

    except IntegrityError as ie:
        db.rollback()
        logger.exception("Integrity error during signup for email=%s: %s", payload.email, ie)
        # If we created an auth user during this request and DB failed, attempt cleanup
        if created_auth_user_id:
            try:
                supabase.auth.admin.delete_user(created_auth_user_id)
            except Exception:
                logger.exception("Failed to delete supabase user %s after integrity error", created_auth_user_id)
        raise HTTPException(status_code=400, detail="Signup failed due to invalid data (integrity error).")

    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected signup error for email=%s: %s", payload.email, exc)
        # If we created the auth user in this request and later steps failed, delete the supabase user
        if created_auth_user_id:
            try:
                supabase.auth.admin.delete_user(created_auth_user_id)
            except Exception:
                logger.exception("Failed to delete supabase user %s after unexpected error", created_auth_user_id)
        # For errors where auth provider already had the user and we attempted linking, don't delete provider user.
        # Return a clear error to the client.
        raise HTTPException(status_code=500, detail="Signup failed due to server error.")

@router.post("/login")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        # 1️⃣ Supabase authentication
        auth_res = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })

        if not getattr(auth_res, "user", None):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = UUID(auth_res.user.id)

        # 2️⃣ Fetch local user profile
        user_profile = (
            db.query(
                schema.Users.user_id,
                schema.Users.name,
                schema.Users.role_id,
                schema.Users.loc_id,
                schema.Role.role_name,
                schema.Location.loc_name,
            )
            .join(schema.Role, schema.Users.role_id == schema.Role.role_id)
            .join(schema.Location, schema.Users.loc_id == schema.Location.loc_id)
            .filter(schema.Users.user_id == user_id)
            .first()
        )

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not initialized. Please sign up first.")

        # 3️⃣ Close old active sessions
        db.query(schema.Sessions).filter(
            schema.Sessions.user_id == user_id,
            schema.Sessions.logout_time.is_(None),
        ).update({"logout_time": datetime.now(IST)})

        # 4️⃣ Create new session
        new_session = schema.Sessions(
            session_id=uuid4(),
            user_id=user_id,
            device="web",
            login_time=datetime.now(IST),
        )
        db.add(new_session)
        db.commit()

        # 5️⃣ Fetch login streak
        streak_row = db.execute(
            text("SELECT streak FROM login_streak_view WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchone()

        # 6️⃣ Award streak bonus from day 2 onward
        if streak_row and streak_row.streak >= 2:
            wallet = db.query(schema.PointWallet).filter(
                schema.PointWallet.user_id == user_id
            ).first()

            if wallet:
                wallet.total_points += 5
                db.add(schema.PointHistory(
                    id=uuid4(),
                    user_id=user_id,
                    points=5,
                    source="Streak",
                ))

                plan_id = db.query(schema.Location.plan_id).filter(
                    schema.Location.loc_id == user_profile.loc_id
                ).scalar()

                db.add(schema.Event(
                    event_id=uuid4(),
                    user_id=user_id,
                    session_id=new_session.session_id,
                    plan_id=plan_id,
                    feature="streak",
                    action="bonus_awarded",
                    timestamp=datetime.now(IST),
                ))
                db.commit()

        # 7️⃣ Return response
        return {
            "access_token": auth_res.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user_profile.user_id),
                "name": user_profile.name,
                "role_id": str(user_profile.role_id),
                "loc_id": str(user_profile.loc_id),
                "role_name": user_profile.role_name,
                "loc_name": user_profile.loc_name,
            },
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.exception("LOGIN ERROR: %s", e)
        raise HTTPException(status_code=500, detail="Login failed due to server error.")
