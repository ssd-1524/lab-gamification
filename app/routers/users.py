from __future__ import annotations

from typing import Dict

from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.models.schema import PointWallet, Sessions, Users
from app.routers.deps import get_db
from app.routers.deps import get_authenticated_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/bootstrap", status_code=status.HTTP_201_CREATED)
def bootstrap_user(
    payload: Dict[str, str],
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Create full user profile after Supabase signup.
    Creates USERS, POINTWALLET and initial SESSION.
    """
    user_id = user["sub"]

    existing_user = db.query(Users).filter(Users.user_id == user_id).first()
    if existing_user:
        return {"status": "exists"}

    try:
        new_user = Users(
            user_id=user_id,
            name=payload["name"],
            role_id=payload["role_id"],
            loc_id=payload["loc_id"],
        )
        db.add(new_user)

        wallet = PointWallet(
            user_id=user_id,
            total_points=0,
            rank="Bronze",
        )
        db.add(wallet)

        session = Sessions(user_id=user_id)
        db.add(session)

        db.commit()
    except KeyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required field: {exc.args[0]}",
        ) from exc

    return {"status": "created"}


@router.get("/me")
def get_me(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Return the authenticated user's profile."""
    user_id = user["sub"]

    db_user = db.query(Users).filter(Users.user_id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    return {
        "user_id": str(db_user.user_id),
        "name": db_user.name,
        "role_id": str(db_user.role_id),
        "loc_id": str(db_user.loc_id),
    }

@router.get("/leaderboard")
def get_leaderboard(
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    uid = identity["user_id"]

    rows = db.execute(
        text("""
            SELECT *,
                   (user_id = :uid) AS is_me
            FROM leaderboard_view
            ORDER BY total_points DESC, updated_at ASC
            LIMIT 20;
        """),
        {"uid": uid},
    ).fetchall()

    return [
        {
            "name": r.name,
            "points": r.total_points,
            "rank": r.rank,
            "badge_image": r.badge_image,
            "is_me": bool(r.is_me),
        }
        for r in rows
    ]

@router.get("/me/rank")
def get_my_rank(
    identity: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    uid = identity["user_id"]

    row = db.execute(
        text("""
            SELECT rank, badge_image, total_points
            FROM leaderboard_view
            WHERE user_id = :uid
        """),
        {"uid": uid},
    ).fetchone()

    position = db.execute(
        text("""
            SELECT COUNT(*) + 1
            FROM leaderboard_view
            WHERE total_points > (
                SELECT total_points FROM leaderboard_view WHERE user_id = :uid
            )
        """),
        {"uid": uid},
    ).scalar()

    if not row:
        return {"rank": None, "badge_image": None, "points": 0, "position": None}

    return {
        "rank": row.rank,
        "badge_image": row.badge_image,
        "points": row.total_points,
        "position": int(position or 1),
    }