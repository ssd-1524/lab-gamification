from app.utils.supabase_client import supabase_client

TIER_BADGES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]

def sync_rank_from_tier_badge(user_id: str):
    # 1. Find tier badge for user
    res = (
        supabase_client
        .table("user_badges")
        .select("badge_id")
        .eq("user_id", user_id)
        .execute()
    )

    if not res.data:
        return None

    badge_ids = [r["badge_id"] for r in res.data]

    tier_res = (
        supabase_client
        .table("badges")
        .select("name")
        .in_("badge_id", badge_ids)
        .in_("name", TIER_BADGES)
        .limit(1)
        .execute()
    )

    if not tier_res.data:
        return None

    tier_name = tier_res.data[0]["name"]

    # 2. Update rank (idempotent)
    supabase_client.table("pointwallet").update({
        "rank": tier_name
    }).eq("user_id", user_id).execute()

    return tier_name
