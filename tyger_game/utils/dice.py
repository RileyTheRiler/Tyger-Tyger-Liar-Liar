import random

def roll(count: int = 2, sides: int = 6) -> int:
    """Simulates rolling n dice with s sides."""
    return sum(random.randint(1, sides) for _ in range(count))

def roll_check(skill_level: int, difficulty: int) -> dict:
    """
    Performs a standard 2d6 check. 
    Returns a dict with details of the roll.
    """
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    base_roll = die1 + die2
    total = base_roll + skill_level
    
    success = total >= difficulty
    is_critical_success = (die1 == 6 and die2 == 6)
    is_critical_failure = (die1 == 1 and die2 == 1)

    # Snake eyes is auto-fail, Boxcars is auto-success (common disco rules, can adjust)
    if is_critical_failure:
        success = False
    elif is_critical_success:
        success = True

    return {
        "die1": die1,
        "die2": die2,
        "base_roll": base_roll,
        "skill_level": skill_level,
        "total": total,
        "difficulty": difficulty,
        "success": success,
        "critical_success": is_critical_success,
        "critical_failure": is_critical_failure
    }
