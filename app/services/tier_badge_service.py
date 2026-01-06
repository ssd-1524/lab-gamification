from app.utils.supabase_client import supabase_client

TIER_BADGES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]

def process_tier_badge_for_user(user_id: str):
    # 1) Get user points
    wallet = (
        supabase_client
        .table("pointwallet")
        .select("total_points")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not wallet.data or wallet.data["total_points"] is None:
        return None

    total_points = wallet.data["total_points"]

    # 2) Highest eligible tier (GLOBAL)
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

    # 3) Fetch existing tier badges (if any)
    existing = (
        supabase_client
        .table("user_badges")
        .select("badge_id")
        .eq("user_id", user_id)
        .execute()
    )

    existing_tier_ids = []
    if existing.data:
        ids = [r["badge_id"] for r in existing.data]
        tiers = (
            supabase_client
            .table("badges")
            .select("badge_id, min_points")
            .in_("badge_id", ids)
            .in_("name", TIER_BADGES)
            .execute()
        )
        existing_tier_ids = [r["badge_id"] for r in tiers.data] if tiers.data else []

    # 4) Revoke all existing tier badges (self-healing)
    if existing_tier_ids:
        supabase_client.table("user_badges").delete().in_("badge_id", existing_tier_ids).eq(
            "user_id", user_id
        ).execute()

    # 5) Award eligible tier
    supabase_client.table("user_badges").insert({
        "user_id": user_id,
        "badge_id": eligible_badge["badge_id"]
    }).execute()

    return eligible_badge["name"]
