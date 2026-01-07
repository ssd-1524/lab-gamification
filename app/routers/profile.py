from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.routers.deps import get_authenticated_user, get_db

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)

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

    user_row = db.execute(
        text("""
            SELECT name
            FROM users
            WHERE user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchone()

    user_name = user_row.name if user_row else "User"

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

    # ---------------- Points History ---------------- #
    points_rows = db.execute(
        text("""
            SELECT
                points,
                source as reason,
                timestamp as created_at
            FROM pointhistory
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 5
        """),
        {"user_id": user_id},
    ).fetchall()

    points_history = [
        {
            "points": row.points,
            "reason": row.reason,
            "date": row.created_at.strftime("%d %b %Y"),
        }
        for row in points_rows
    ]

    # ---------------- Final Payload ---------------- #
    return {
        "user": {
            "user_id": user_id,
            "name": user_name,
        },
        "wallet": {
            "total_points": total_points,
            "rank": rank,
        },
        "badges": badges,
        "points_history": points_history,
    }
