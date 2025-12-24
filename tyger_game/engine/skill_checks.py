from tyger_game.utils.dice import roll_check
from tyger_game.engine.character import Character

class CheckResult:
    def __init__(self, success: bool, total: int, details: dict, check_type: str):
        self.success = success
        self.total = total
        self.details = details
        self.check_type = check_type # 'red' or 'white'

def perform_skill_check(character: Character, skill_name: str, difficulty: int, check_type: str = 'white') -> CheckResult:
    """
    Performs a skill check for the character.
    """
    skill_level = character.get_skill_level(skill_name)
    
    # Use the util dice function
    roll_details = roll_check(skill_level, difficulty)
    
    result = CheckResult(
        success=roll_details['success'],
        total=roll_details['total'],
        details=roll_details,
        check_type=check_type
    )
    
    return result

def format_check_result(result: CheckResult) -> str:
    """Returns a readable string for the check result."""
    d = result.details
    outcome = "SUCCESS" if result.success else "FAILURE"
    crit = ""
    if d['critical_success']: crit = " (CRITICAL!)"
    if d['critical_failure']: crit = " (CATASTROPHE!)"
    
    return f"[{outcome}{crit}] Rolled {d['base_roll']} + {d['skill_level']} (Skill) = {d['total']} vs DC {d['difficulty']}"
