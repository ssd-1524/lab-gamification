import time
from app.database import SessionLocal
from app.services.badge_service import BadgeService
from sqlalchemy import text


SLEEP_SECONDS = 30


def run_badge_worker():
    """
    Continuous background worker.
    """

    while True:
        db = SessionLocal()
        try:
            service = BadgeService(db)

            # Fetch all users (minimal data)
            user_rows = db.execute(
                text("SELECT user_id FROM users")
            ).fetchall()

            for row in user_rows:
                service._evaluate_user_badges(row.user_id)

        except Exception as e:
            # log error (never crash loop)
            print("Badge worker error:", e)

        finally:
            db.close()

        time.sleep(SLEEP_SECONDS)
