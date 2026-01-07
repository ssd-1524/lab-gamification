from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID


class BadgeService:
    """
    Central service for evaluating and awarding badges.
    This service is called ONLY from background workers.
    """
    CLUTCH_COMMANDER_MAX_RESPONSE_SEC = 1800
    LOGIN_STREAK_REQUIRED_DAYS = 10
    QUIZ_MASTER_REQUIRED_DAYS = 5
    QUIZ_MAX_SCORE = 30

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # PUBLIC ENTRY POINT
    # ==================================================
    def _evaluate_user_badges(self, user_id: UUID) -> None:
        self._evaluate_login_streak_badge(user_id)
        self._evaluate_quiz_master_badge(user_id)
        self._evaluate_monthly_mvp_badge(user_id)
        self._evaluate_clutch_commander_badge(user_id)

    # ==================================================
    # CLUTCH COMMANDER BADGE
    # ==================================================
    def _evaluate_clutch_commander_badge(self, user_id: UUID) -> None:
        if not self._has_fast_anomaly_response(user_id):
            return

        badge_id = self._get_badge_id_by_name("Clutch Commander")
        if not badge_id:
            return

        if self._user_already_has_badge(user_id, badge_id):
            return

        self._award_badge(user_id, badge_id)

    def _has_fast_anomaly_response(self, user_id: UUID) -> bool:
        query = text("""
            SELECT 1
            FROM events
            WHERE user_id = :user_id
            AND feature = 'anomaly'
            AND action = 'accepted'
            AND (metadata->>'response_time_sec')::numeric <= :max_seconds
            LIMIT 1
        """)

        return (
            self.db.execute(
                query,
                {
                    "user_id": user_id,
                    "max_seconds": self.CLUTCH_COMMANDER_MAX_RESPONSE_SEC,
                },
            ).fetchone()
            is not None
        )


    # ==================================================
    # LOGIN STREAK BADGE (Sweet Loyalty)
    # ==================================================
    def _evaluate_login_streak_badge(self, user_id: UUID) -> None:
        streak = self._get_user_login_streak(user_id)

        if streak < self.LOGIN_STREAK_REQUIRED_DAYS:
            return

        badge_id = self._get_badge_id_by_name("Sweet Loyalty")
        if not badge_id:
            return

        if self._user_already_has_badge(user_id, badge_id):
            return

        self._award_badge(user_id, badge_id)

    def _get_user_login_streak(self, user_id: UUID) -> int:
        query = text("""
            SELECT streak
            FROM login_streak_view
            WHERE user_id = :user_id
        """)

        row = self.db.execute(query, {"user_id": user_id}).fetchone()
        return row[0] if row else 0

    # ==================================================
    # QUIZ MASTER BADGE
    # ==================================================
    def _evaluate_quiz_master_badge(self, user_id: UUID) -> None:
        if not self._has_consecutive_perfect_quiz_days(user_id):
            return

        badge_id = self._get_badge_id_by_name("Quiz Master")
        if not badge_id:
            return

        if self._user_already_has_badge(user_id, badge_id):
            return

        self._award_badge(user_id, badge_id)

    def _has_consecutive_perfect_quiz_days(self, user_id: UUID) -> bool:
        query = text("""
            WITH quiz_days AS (
                SELECT
                    timestamp::date AS quiz_date,
                    (metadata->>'score')::int AS score,
                    (metadata->>'max_score')::int AS max_score
                FROM events
                WHERE user_id = :user_id
                  AND feature = 'quiz'
                  AND action = 'completed'
            ),
            perfect_days AS (
                SELECT quiz_date
                FROM quiz_days
                WHERE score = max_score
                  AND max_score = :max_score
            ),
            streak_groups AS (
                SELECT
                    quiz_date,
                    quiz_date - (ROW_NUMBER() OVER (ORDER BY quiz_date) * INTERVAL '1 day') AS grp
                FROM perfect_days
            )

            SELECT COUNT(*) >= :required_days
            FROM streak_groups
            GROUP BY grp
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """)

        result = self.db.execute(
            query,
            {
                "user_id": user_id,
                "max_score": self.QUIZ_MAX_SCORE,
                "required_days": self.QUIZ_MASTER_REQUIRED_DAYS,
            },
        ).scalar()

        return bool(result)
    
    def _evaluate_monthly_mvp_badge(self, user_id: UUID) -> None:
        # 🚫 Only run on last day of the month (IST)
        if not self._is_last_day_of_month():
            return

        if not self._is_user_monthly_top_scorer(user_id):
            return

        badge_id = self._get_badge_id_by_name("Monthly MVP")
        if not badge_id:
            return

        if self._user_already_has_badge(user_id, badge_id):
            return

        self._award_badge(user_id, badge_id)



    # ==================================================
    # SHARED HELPERS
    # ==================================================
    def _get_badge_id_by_name(self, badge_name: str) -> UUID | None:
        query = text("""
            SELECT badge_id
            FROM badges
            WHERE name = :name
            LIMIT 1
        """)

        row = self.db.execute(query, {"name": badge_name}).fetchone()
        return row[0] if row else None

    def _user_already_has_badge(self, user_id: UUID, badge_id: UUID) -> bool:
        query = text("""
            SELECT 1
            FROM user_badges
            WHERE user_id = :user_id
              AND badge_id = :badge_id
            LIMIT 1
        """)

        return (
            self.db.execute(
                query,
                {"user_id": user_id, "badge_id": badge_id},
            ).fetchone()
            is not None
        )

    def _award_badge(self, user_id: UUID, badge_id: UUID) -> None:
        query = text("""
            INSERT INTO user_badges (user_id, badge_id, earned_at)
            VALUES (:user_id, :badge_id, timezone('Asia/Kolkata', now()))
        """)

        self.db.execute(query, {"user_id": user_id, "badge_id": badge_id})
        self.db.commit()

    def _is_user_monthly_top_scorer(self, user_id: UUID) -> bool:
        """
        Determines if the user has the highest total points
        accumulated in the current month.
        """

        query = text("""
            WITH monthly_points AS (
                SELECT
                    ph.user_id,
                    SUM(ph.points) AS total_points
                FROM pointhistory ph
                WHERE date_trunc('month', ph.timestamp)
                    = date_trunc('month', timezone('Asia/Kolkata', now()))
                GROUP BY ph.user_id
            ),
            ranked_users AS (
                SELECT
                    user_id,
                    total_points,
                    RANK() OVER (ORDER BY total_points DESC) AS rnk
                FROM monthly_points
            )
            SELECT user_id
            FROM ranked_users
            WHERE rnk = 1
            LIMIT 1
        """)

        row = self.db.execute(query).fetchone()
        return row is not None and row[0] == user_id
        
    def _is_last_day_of_month(self) -> bool:
        query = text("""
            SELECT
                current_date =
                (date_trunc('month', current_date)
                + INTERVAL '1 month'
                - INTERVAL '1 day')::date
        """)

        return bool(self.db.execute(query).scalar())
