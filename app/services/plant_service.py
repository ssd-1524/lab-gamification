# app/services/plant_service.py

def get_plant_stage(streak: int, longest_streak: int) -> str:
    """
    Decide plant stage using current and historical streaks.

    Logic:
    - streak > 0  → growing plant
    - streak = 0 & longest_streak = 0 → new user → soil
    - streak = 0 & longest_streak > 0 → streak broken → dead
    """

    if streak > 0:
        if streak <= 5:
            return "small"
        if streak <= 10:
            return "medium"
        return "large"

    # streak == 0
    if longest_streak == 0:
        return "soil"

    return "dead"
