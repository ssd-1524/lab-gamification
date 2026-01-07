# app/services/tier_badge_service.py
"""
Tier badge assignment service for Stomata Labs.

This module:
- Reads a user's total points from pointwallet.
- Finds the highest eligible tier badge from badges.
- Removes any lower-tier badges for the user.
- Awards the highest eligible tier (idempotent / safe against duplicates).
- Returns the awarded badge name or None.

Defensive behavior:
- Handles None responses from supabase_client.execute()
- Handles responses that are either objects with `.data` or dicts with ["data"]
- Logs Supabase errors and returns None on unexpected failures
- Attempts to ignore unique-constraint duplicate insert errors
"""

from typing import Any, Dict, List, Optional
import logging
import re

from app.utils.supabase_client import supabase_client

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TIER_BADGES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]


def _resp_data(resp: Any) -> Optional[Any]:
    """
    Safely extract `data` from a Supabase response which may be:
      - an object with `.data` and `.error` attributes
      - a dict with 'data' and 'error' keys
      - None

    Returns the data (or None).
    """
    if resp is None:
        return None
    # object-style response (supabase-py vX)
    if hasattr(resp, "data"):
        return getattr(resp, "data")
    # dict-style response
    if isinstance(resp, dict):
        return resp.get("data")
    return None


def _resp_error(resp: Any) -> Optional[Any]:
    if resp is None:
        return None
    if hasattr(resp, "error"):
        return getattr(resp, "error")
    if isinstance(resp, dict):
        return resp.get("error")
    return None


def _is_unique_violation_error(err: Any) -> bool:
    """
    Try to detect a unique constraint violation in the returned error.
    Supabase / Postgres error shapes vary; look for typical keywords.
    """
    if not err:
        return False
    # error object may be dict or string
    if isinstance(err, str):
        err_text = err
    elif isinstance(err, dict):
        # err dict may contain 'message' or 'details'
        err_text = err.get("message") or err.get("details") or str(err)
    else:
        err_text = str(err)

    # common Postgres unique constraint phrases
    return bool(re.search(r"unique|duplicate|already exists|unique constraint", err_text, re.IGNORECASE))


def process_tier_badge_for_user(user_id: str) -> Optional[str]:
    """
    Compute and assign the highest eligible tier badge for the given user_id.

    Returns:
      - badge name (e.g., "Gold") if awarded or already present
      - None if no eligible badge or on error
    """
    try:
        # 1️⃣ Fetch wallet
        resp_wallet = (
            supabase_client
            .table("pointwallet")
            .select("total_points")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        wallet_data = _resp_data(resp_wallet)
        wallet_err = _resp_error(resp_wallet)
        if wallet_err:
            logger.warning("Supabase wallet fetch error for user %s: %s", user_id, wallet_err)

        if not wallet_data or wallet_data.get("total_points") is None:
            # nothing to do if wallet missing or total_points missing
            logger.debug("No wallet/points found for user %s", user_id)
            return None

        total_points = wallet_data["total_points"]

        # 2️⃣ Highest eligible tier
        resp_eligible = (
            supabase_client
            .table("badges")
            .select("badge_id, name, min_points")
            .in_("name", TIER_BADGES)
            .lte("min_points", total_points)
            .order("min_points", desc=True)
            .limit(1)
            .execute()
        )
        eligible_data = _resp_data(resp_eligible)
        eligible_err = _resp_error(resp_eligible)
        if eligible_err:
            logger.warning("Supabase badges fetch error for user %s: %s", user_id, eligible_err)

        if not eligible_data:
            # user not eligible for any tier badges
            logger.debug("No eligible tier badge for user %s with points=%s", user_id, total_points)
            return None

        # eligible_data may be a list with one row
        eligible_badge = eligible_data[0] if isinstance(eligible_data, list) else eligible_data
        eligible_badge_id = eligible_badge.get("badge_id")
        eligible_badge_name = eligible_badge.get("name")
        eligible_min_points = eligible_badge.get("min_points")

        if not eligible_badge_id:
            logger.error("Malformed eligible badge data for user %s: %s", user_id, eligible_badge)
            return None

        # 3️⃣ Does user already have this badge?
        resp_exists = (
            supabase_client
            .table("user_badges")
            .select("badge_id")
            .eq("user_id", user_id)
            .eq("badge_id", eligible_badge_id)
            .maybe_single()
            .execute()
        )
        exists_data = _resp_data(resp_exists)
        exists_err = _resp_error(resp_exists)
        if exists_err:
            logger.warning("Supabase user_badges exists check error for user %s: %s", user_id, exists_err)

        if exists_data:
            # user already has the eligible badge — idempotent success
            logger.debug("User %s already has badge %s", user_id, eligible_badge_name)
            return eligible_badge_name

        # 4️⃣ Remove lower tier badges only (if present)
        resp_old_tiers = (
            supabase_client
            .table("badges")
            .select("badge_id")
            .in_("name", TIER_BADGES)
            .lt("min_points", eligible_min_points)
            .execute()
        )
        old_tiers_data = _resp_data(resp_old_tiers)
        old_tiers_err = _resp_error(resp_old_tiers)
        if old_tiers_err:
            logger.warning("Supabase old_tiers fetch error for user %s: %s", user_id, old_tiers_err)

        if old_tiers_data:
            old_ids = [r["badge_id"] for r in old_tiers_data if r.get("badge_id")]
            if old_ids:
                del_resp = (
                    supabase_client
                    .table("user_badges")
                    .delete()
                    .eq("user_id", user_id)
                    .in_("badge_id", old_ids)
                    .execute()
                )
                del_err = _resp_error(del_resp)
                if del_err:
                    logger.warning("Failed to delete old badges for user %s: %s", user_id, del_err)

        # 5️⃣ Award new tier safely
        insert_payload = {"user_id": user_id, "badge_id": eligible_badge_id}
        insert_resp = supabase_client.table("user_badges").insert(insert_payload).execute()
        insert_err = _resp_error(insert_resp)
        if insert_err:
            # if unique-violation, treat as success (concurrent award or previously awarded)
            if _is_unique_violation_error(insert_err):
                logger.info("Badge already assigned (unique violation) for user %s badge %s", user_id, eligible_badge_name)
                return eligible_badge_name
            # other errors -> log and return None
            logger.error("Failed to insert user_badges for user %s: %s", user_id, insert_err)
            return None

        # success
        logger.info("Awarded badge %s to user %s", eligible_badge_name, user_id)
        return eligible_badge_name

    except Exception as exc:
        # catch-all to avoid bubbling NoneType attribute errors to callers and to capture unexpected failures
        logger.exception("Unexpected error while processing tier badge for user %s: %s", user_id, exc)
        return None
