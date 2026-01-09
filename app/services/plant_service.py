def get_plant_stage(
    streak: int,
    longest_streak: int,
    has_replanted_after_break: bool,
) -> str:
    """
    Final plant growth logic.
 
    - Growing if streak > 0
    - Soil if user replanted after streak ended
    - Soil if user never had a streak
    - Dead otherwise
    """
 
    if streak > 0:
        if streak <= 5:
            return "small"
        if streak <= 10:
            return "medium"
        return "large"
 
    if has_replanted_after_break:
        return "soil"
 
    if longest_streak == 0:
        return "soil"
 
    return "dead"
 
 