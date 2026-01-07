from app.utils.supabase_client import supabase_client

TIER_BADGES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]


def process_tier_badge_for_user(user_id: str):
    # 1️⃣ Fetch wallet
    wallet = (
        supabase_client
        .table("pointwallet")
        .select("total_points")
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not wallet or not wallet.data or wallet.data.get("total_points") is None:
        return None


    total_points = wallet.data["total_points"]

    # 2️⃣ Highest eligible tier
    eligible = (
        supabase_client
        .table("badges")
        .select("badge_id, name, min_points")
        .in_("name", TIER_BADGES)
        .lte("min_points", total_points)
        .order("min_points", desc=True)
        .limit(1)
        .execute()
    )

    if not eligible.data:
        return None

    eligible_badge = eligible.data[0]
    eligible_badge_id = eligible_badge["badge_id"]

    # 3️⃣ Does user already have this badge?
    exists = (
        supabase_client
        .table("user_badges")
        .select("badge_id")
        .eq("user_id", user_id)
        .eq("badge_id", eligible_badge_id)
        .maybe_single()
        .execute()
    )

    if exists.data:
        return eligible_badge["name"]  # nothing to do

    # 4️⃣ Remove lower tier badges only
    old_tiers = (
        supabase_client
        .table("badges")
        .select("badge_id")
        .in_("name", TIER_BADGES)
        .lt("min_points", eligible_badge["min_points"])
        .execute()
    )

    if old_tiers.data:
        old_ids = [r["badge_id"] for r in old_tiers.data]
        supabase_client.table("user_badges") \
            .delete() \
            .eq("user_id", user_id) \
            .in_("badge_id", old_ids) \
            .execute()

    # 5️⃣ Award new tier safely
    supabase_client.table("user_badges").insert({
        "user_id": user_id,
        "badge_id": eligible_badge_id
    }).execute()

    return eligible_badge["name"]
