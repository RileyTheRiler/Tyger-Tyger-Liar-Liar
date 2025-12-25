import random
from typing import Tuple, Dict

def roll_2d6(manual_roll: int = None) -> Dict:
    """
    Rolls 2d6 and returns a dictionary with results.
    Handles manual overrides for testing/debug.
    """
    if manual_roll is not None:
        # For manual override, we simulate the two dice
        d1 = manual_roll // 2
        d2 = manual_roll - d1
        return {
            "d1": d1,
            "d2": d2,
            "total": manual_roll,
            "is_double": d1 == d2,
            "is_critical_success": manual_roll == 12,
            "is_critical_failure": manual_roll == 2,
            "is_manual": True
        }
    
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    
    return {
        "d1": d1,
        "d2": d2,
        "total": total,
        "is_double": d1 == d2,
        "is_critical_success": total == 12,
        "is_critical_failure": total == 2,
        "is_manual": False
    }

def get_roll_description(roll_data: Dict) -> str:
    """Returns a flavor description of the natural roll."""
    total = roll_data["total"]
    
    if total == 12:
        return "CRITICAL SUCCESS! A perfect perception of reality."
    if total == 2:
        return "CRITICAL FAILURE! The logic collapses into static."
    if roll_data["is_double"]:
        return f"Doubles ({roll_data['d1']}s). A moment of heightened resonance."
    
    return ""
