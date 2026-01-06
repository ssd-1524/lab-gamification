from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from sqlalchemy import text
from datetime import datetime
import uuid

from datetime import datetime, timedelta
import pytz
from app.routers.deps import get_db, get_authenticated_user
from app.models import schema
from app.utils.auth import supabase
from pydantic import BaseModel, EmailStr

IST = pytz.timezone("Asia/Kolkata")
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------- Request Schemas ----------

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: UUID
    loc_id: UUID


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- Endpoints ----------

@router.post("/signup/")
async def signup(payload: UserSignup, db: Session = Depends(get_db)):
    auth_user_id = None
    try:
        auth_res = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })

        if not auth_res.user:
            raise HTTPException(status_code=400, detail="Supabase signup failed")

        auth_user_id = auth_res.user.id
        user_uuid = UUID(auth_user_id)

        new_user = schema.Users(
            user_id=user_uuid,
            name=payload.name,
            role_id=payload.role_id,
            loc_id=payload.loc_id,
        )
        db.add(new_user)
        db.flush()

        new_wallet = schema.PointWallet(
            user_id=user_uuid,
            total_points=0,
            rank="Bronze",
        )
        db.add(new_wallet)

        db.commit()
        return {"status": "success", "user_id": str(user_uuid)}

    except Exception as e:
        db.rollback()
        if auth_user_id:
            try:
                supabase.auth.admin.delete_user(auth_user_id)
            except Exception:
                pass
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        # 1. Supabase auth
        auth_res = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })

        if not auth_res.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = UUID(auth_res.user.id)

        # 2. Fetch local profile
        user_profile = (
            db.query(
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
            raise HTTPException(status_code=404, detail="User profile not found")

        # 3. Close any previous active sessions
        db.query(schema.Sessions).filter(
            schema.Sessions.user_id == user_id,
            schema.Sessions.logout_time.is_(None),
        ).update({"logout_time": datetime.now(IST)})

        # 4. Create new active session
        

        new_session = schema.Sessions(
            session_id=uuid.uuid4(),
            user_id=user_id,
            device="web",
            login_time=datetime.now(IST),
        )
        db.add(new_session)
        db.commit()

        # ---- LOGIN STREAK BONUS ----
        streak_row = db.execute(
            text("SELECT streak FROM login_streak_view WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchone()

        if streak_row and streak_row.streak >= 1:
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

                # Fetch real plan_id from locations table
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

        return {
            "access_token": auth_res.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user_id),
                "name": user_profile.name,
                "role_id": str(user_profile.role_id),
                "loc_id": str(user_profile.loc_id),
                "role_name": user_profile.role_name,
                "loc_name": user_profile.loc_name,
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/points")
def get_my_points(
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    user_id = identity["user_id"]

    wallet = (
        db.query(schema.PointWallet)
        .filter(schema.PointWallet.user_id == user_id)
        .first()
    )

    return {
        "total_points": wallet.total_points if wallet else 0,
        "rank": wallet.rank if wallet else None,
    }
