from datetime import datetime


def get_plant_state(
    streak: int,
    longest_streak: int,
    replanted_at: datetime | None,
    last_login: datetime | None,
) -> str:
    """
    Plant stage rules:

    - If user replanted AFTER the last login → soil
    - If streak > 0 → growing plant
    - If streak == 0 and longest_streak == 0 → soil (new user)
    - If streak == 0 and longest_streak > 0 → dead plant
    """

    # 🌱 User explicitly replanted after streak break
    if replanted_at and last_login and replanted_at > last_login:
        return "soil"

    # 🌿 Growing
    if streak > 0:
        if streak <= 5:
            return "small"
        if streak <= 10:
            return "medium"
        return "large"

    # 🟤 Brand new user
    if longest_streak == 0:
        return "soil"

    # ☠️ Streak broken & not replanted
    return "dead"
