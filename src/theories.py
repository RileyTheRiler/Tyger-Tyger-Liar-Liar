
THEORY_DATA = {
    "i_want_to_believe": {
        "name": "I Want To Believe",
        "category": "Belief",
        "description": "You're starting to think... maybe it's not all explainable.",
        "hidden_effects": True,
        "effects": {
            "Paranormal Sensitivity": 2,
            "Instinct": 1,
            "Logic": -1,
            "Skepticism": -1
        },
        "conflicts_with": ["there_is_a_rational_explanation"],
        "internalize_time_hours": 6,
        "active_case": False
    },
    "there_is_a_rational_explanation": {
        "name": "There's A Rational Explanation",
        "category": "Skepticism",
        "description": "Everything has a cause. Physics doesn't just break.",
        "hidden_effects": True,
        "effects": {
            "Logic": 2,
            "Forensics": 1,
            "Paranormal Sensitivity": -2,
            "Instinct": -1
        },
        "conflicts_with": ["i_want_to_believe"],
        "internalize_time_hours": 6,
        "active_case": False
    },
    "trust_no_one": {
        "name": "Trust No One",
        "category": "Conspiracy",
        "description": "They are watching. They are always watching.",
        "hidden_effects": True,
        "effects": {
            "Perception": 2,
            "Skepticism": 1,
            "Charm": -2,
            "Authority": -1
        },
        "conflicts_with": [],
        "internalize_time_hours": 8,
        "active_case": False
    },
    "follow_the_evidence": {
        "name": "Follow the Evidence",
        "category": "Investigation Style",
        "description": "The truth is in the details, not your feelings.",
        "hidden_effects": False,
        "effects": {
            "Forensics": 2,
            "Research": 1,
            "Instinct": -1
        },
        "conflicts_with": ["trust_your_gut"],
        "internalize_time_hours": 4,
        "active_case": False
    },
    "trust_your_gut": {
        "name": "Trust Your Gut",
        "category": "Investigation Style",
        "description": "Your subconscious knows things your eyes missed.",
        "hidden_effects": False,
        "effects": {
            "Instinct": 2,
            "Pattern Recognition": 1,
            "Logic": -1
        },
        "conflicts_with": ["follow_the_evidence"],
        "internalize_time_hours": 4,
        "active_case": False
    },
    "the_missing_are_connected": {
        "name": "The Missing Are Connected",
        "category": "Active Case",
        "description": "It's not a coincidence. It's a pattern.",
        "hidden_effects": True,
        "effects": {
            "Pattern Recognition": 3,
            "Research": 1,
            "Composure": -1
        },
        "conflicts_with": [],
        "internalize_time_hours": 12,
        "active_case": True
    },
    "what_happened_in_town": {
        "name": "What Happened In Blackwood",
        "category": "Trauma",
        "description": "You can't forget the smell of the smoke.",
        "hidden_effects": False,
        "effects": {
            "Endurance": 1,
            "Composure": -2,
            "Empathy": 1
        },
        "conflicts_with": [],
        "internalize_time_hours": 10,
        "active_case": False
    }
}
