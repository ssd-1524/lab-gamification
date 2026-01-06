import time
from app.utils.supabase_client import supabase_client
from app.services.tier_badge_service import process_tier_badge_for_user

SLEEP_SECONDS = 30

def run_tier_badge_worker():
    while True:
        try:
            users = (
                supabase_client
                .table("users")
                .select("user_id")
                .execute()
            )

            for u in users.data or []:
                uid = u.get("user_id")
                if not uid:
                    continue
                try:
                    process_tier_badge_for_user(uid)
                except Exception as e:
                    print(f"⚠️ user {uid}: {e}")
        except Exception as e:
            print(f"❌ worker error: {e}")

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    run_tier_badge_worker()
