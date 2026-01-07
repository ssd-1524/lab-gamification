from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.routers.deps import get_authenticated_user, get_db

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


# ---------------- DB Dependency ---------------- #

get_db()

# ---------------- Profile API ---------------- #

@router.get("/me")
def get_my_profile(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Fetch profile details for the logged-in user.
    """

    user_id = user["user_id"]

    # ---------------- Wallet & Rank ---------------- #
    wallet_row = db.execute(
        text("""
            SELECT
                total_points,
                rank
            FROM pointwallet
            WHERE user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchone()

    total_points = wallet_row.total_points if wallet_row else 0
    rank = wallet_row.rank if wallet_row else None

    # ---------------- Badges ---------------- #
    badge_rows = db.execute(
        text("""
            SELECT
                b.name,
                b.images,
                ub.earned_at
            FROM user_badges ub
            JOIN badges b
              ON b.badge_id = ub.badge_id
            WHERE ub.user_id = :user_id
            ORDER BY ub.earned_at DESC
        """),
        {"user_id": user_id},
    ).fetchall()

    badges = [
        {
            "name": row.name,
            "images": row.images,
            "earned_at": row.earned_at,
        }
        for row in badge_rows
    ]

    # ---------------- Final Payload ---------------- #
    return {
        "user": {
            "user_id": user_id,
            "name": user.get("name"),
        },
        "wallet": {
            "total_points": total_points,
            "rank": rank,
        },
        "badges": badges,
    }
