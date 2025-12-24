# Attribute Constants
ATTRIBUTES = [
    "REASON",
    "INTUITION",
    "CONSTITUTION",
    "PRESENCE"
]

# Skill Constants
SKILLS = {
    "REASON": [
        "Logic", "Encyclopedia", "Rhetoric", "Drama", "Conceptualization", "Visual Calculus"
    ],
    "INTUITION": [
        "Volition", "Inland Empire", "Empathy", "Authority", "Esprit de Corps", "Suggestion"
    ],
    "CONSTITUTION": [
        "Endurance", "Pain Threshold", "Physical Instrument", "Electrochemistry", "Shivers"
    ],
    "PRESENCE": [
        "Hand/Eye Coordination", "Perception", "Reaction Speed", "Savoir Faire", "Interfacing", "Composure"
    ]
}

# Game Constants
MAX_SANITY = 100
MAX_REALITY = 100

# UI Colors (ANSI)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
