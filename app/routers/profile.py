from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.routers.deps import get_authenticated_user, get_db
from app.services.plant_service import get_plant_stage
from app.services.plant_config import PLANT_STAGE_CONFIG

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)

# ---------------- Profile API ---------------- #

@router.get("/me/details")
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

@router.get("/plant-state")
def get_plant_state(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    user_id = user["user_id"]
 
    # 1️⃣ Fetch streak data from v2 view (NOW includes last_day)
    streak_row = db.execute(
        text("""
            SELECT
                streak,
                longest_streak,
                last_day
            FROM login_streak_view_v2
            WHERE user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchone()
 
    streak = streak_row.streak if streak_row else 0
    longest_streak = streak_row.longest_streak if streak_row else 0
    last_streak_day = streak_row.last_day if streak_row else None
 
    # 2️⃣ Fetch last replant time
    replant_row = db.execute(
        text("""
            SELECT MAX(timestamp) AS replanted_at
            FROM events
            WHERE user_id = :user_id
              AND feature = 'plant'
              AND action = 'replant_clicked'
        """),
        {"user_id": user_id},
    ).fetchone()
 
    replanted_at = replant_row.replanted_at if replant_row else None
 
    # 3️⃣ Decide replant validity (STABLE & CORRECT)
    has_replanted_after_break = (
        replanted_at is not None
        and last_streak_day is not None
        and replanted_at.date() > last_streak_day
    )
 
    # 4️⃣ Decide plant stage
    plant_stage = get_plant_stage(
        streak,
        longest_streak,
        has_replanted_after_break,
    )
 
    plant_ui = PLANT_STAGE_CONFIG[plant_stage]
 
    return {
        "streak": streak,
        "plant_stage": plant_stage,
        "image_url": plant_ui["image_url"],
        "message": plant_ui["message"],
        "can_replant": plant_ui["can_replant"],
    }