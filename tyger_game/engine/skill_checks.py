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

    return result

SKILL_VOICES = {
    # Rationality
    "Deduction": "The Cold Logic",
    "Encyclopedia": "The Archive",
    "Forensics": "The Mortician",
    "Protocol": "The Bureaucracy",
    "Skepticism": "The Doubt",
    "Tech-Gnosis": "The Machine spirit",
    # Sensitivity
    "Instinct": "The Lizard Brain",
    "Empathy": "The Human Heart",
    "Paranormal Sense": "The Third Eye",
    "Pattern Recognition": "The Red String",
    "Suggestion": "The Silver Tongue",
    "Willpower": "The Shield",
    # Presence
    "Authority": "The Badge",
    "Subterfuge": "The Mask",
    "Negotiation": "The Olive Branch",
    "Esprit de Corps": "The Partner",
    "Interrogation": "The Spotlight",
    "Cool": "The Ice",
    # Fieldcraft
    "Ballistics": "The Trajectory",
    "Pursuit": "The Hunter",
    "Survival": "The Survivor",
    "Perception": "The Open Eye",
    "Force": "The Hammer",
    "Equilibrium": "The Fulcrum"
}

def format_check_result(result: CheckResult, skill_name: str) -> str:
    """Returns a readable string for the check result."""
    d = result.details
    outcome = "SUCCESS" if result.success else "FAILURE"
    crit = ""
    if d['critical_success']: crit = " (CRITICAL!)"
    if d['critical_failure']: crit = " (CATASTROPHE!)"
    
    voice = SKILL_VOICES.get(skill_name, "The Skill")
    
    return f"[{voice}] {outcome}{crit} | Rolled {d['base_roll']} + {d['skill_level']} = {d['total']} vs DC {d['difficulty']}"
