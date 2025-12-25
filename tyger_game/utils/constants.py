# Attribute Constants
ATTRIBUTES = [
    "RATIONALITY",
    "SENSITIVITY",
    "PRESENCE",
    "FIELDCRAFT"
]

# Skill Constants
SKILLS = {
    "RATIONALITY": [
        "Deduction", "Encyclopedia", "Forensics", "Protocol", "Skepticism", "Tech-Gnosis"
    ],
    "SENSITIVITY": [
        "Instinct", "Empathy", "Paranormal Sense", "Pattern Recognition", "Suggestion", "Willpower"
    ],
    "PRESENCE": [
        "Authority", "Subterfuge", "Negotiation", "Esprit de Corps", "Interrogation", "Cool"
    ],
    "FIELDCRAFT": [
        "Ballistics", "Pursuit", "Survival", "Perception", "Force", "Equilibrium"
    ]
}

# Alignment Constants
ALIGNMENTS = {
    "FUNDAMENTALIST": "Fundamentalist",   # Believer + Order
    "TRUTH_SEEKER": "Truth-Seeker",       # Believer + Chaos
    "DEBUNKER": "Debunker",               # Skeptic + Order
    "OPPORTUNIST": "Opportunist"          # Skeptic + Chaos
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
