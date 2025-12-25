

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
        "auto_locks": ["there_is_a_rational_explanation"],
        "degradation_rate": 15,
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
        "auto_locks": ["i_want_to_believe"],
        "degradation_rate": 15,
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
        "conflicts_with": ["conspiracy_of_kindness"],
        "auto_locks": ["conspiracy_of_kindness"],
        "degradation_rate": 10,
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
        "auto_locks": [],
        "degradation_rate": 12,
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
        "auto_locks": [],
        "degradation_rate": 12,
        "internalize_time_hours": 4,
        "active_case": False
    },
    "the_missing_are_connected": {
        "name": "The Missing Are Connected",
        "category": "Active Case",
        "description": "It's not a coincidence. It's a pattern.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Pattern Recognition": 3,
            "Research": 1,
            "Composure": -1
        },
        "conflicts_with": [],
        "auto_locks": [],
        "degradation_rate": 8,
        "internalize_time_hours": 12,
        "active_case": True,
        "critical_for_endgame": True
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
        "auto_locks": [],
        "degradation_rate": 5,
        "internalize_time_hours": 10,
        "active_case": False,
        "critical_for_endgame": True
    },
    "conspiracy_of_kindness": {
        "name": "Conspiracy of Kindness",
        "category": "Trust",
        "description": "Not everyone is out to get you. Some people genuinely want to help.",
        "hidden_effects": False,
        "effects": {
            "Charm": 2,
            "Empathy": 2,
            "Perception": -2,
            "Skepticism": -1
        },
        "conflicts_with": ["trust_no_one"],
        "auto_locks": ["trust_no_one"],
        "degradation_rate": 10,
        "internalize_time_hours": 6,
        "active_case": False
    },
    "the_entity_is_hostile": {
        "name": "The Entity Is Hostile",
        "category": "Belief",
        "description": "The aurora isn't just lights. It's hunting.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Paranormal Sensitivity": 3,
            "Survival": 2,
            "Composure": -2
        },
        "conflicts_with": ["the_entity_is_neutral", "there_is_a_rational_explanation"],
        "auto_locks": [],
        "degradation_rate": 20,
        "internalize_time_hours": 8,
        "active_case": False,
        "critical_for_endgame": True
    },
    "the_entity_is_neutral": {
        "name": "The Entity Is Neutral",
        "category": "Skepticism",
        "description": "It's not malicious. It's just... different. Operating on rules we don't understand.",
        "hidden_effects": True,
        "effects": {
            "Logic": 2,
            "Paranormal Sensitivity": 1,
            "Composure": 1
        },
        "conflicts_with": ["the_entity_is_hostile"],
        "auto_locks": [],
        "degradation_rate": 18,
        "internalize_time_hours": 10,
        "active_case": False,
        "critical_for_endgame": True
    },
    "kaltvik_is_a_prison": {
        "name": "Kaltvik Is A Prison",
        "category": "Conspiracy",
        "description": "347 people. Always 347. They can't leave. We can't leave.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Pattern Recognition": 3,
            "Perception": 2,
            "Composure": -3
        },
        "conflicts_with": ["kaltvik_is_a_sanctuary"],
        "auto_locks": [],
        "degradation_rate": 15,
        "internalize_time_hours": 12,
        "active_case": True,
        "critical_for_endgame": True
    },
    "kaltvik_is_a_sanctuary": {
        "name": "Kaltvik Is A Sanctuary",
        "category": "Belief",
        "description": "They're not trapped. They're protected. The Entity keeps something worse OUT.",
        "hidden_effects": True,
        "effects": {
            "Paranormal Sensitivity": 2,
            "Empathy": 2,
            "Logic": -2
        },
        "conflicts_with": ["kaltvik_is_a_prison"],
        "auto_locks": [],
        "degradation_rate": 18,
        "internalize_time_hours": 14,
        "active_case": False,
        "critical_for_endgame": True
    },
    # === VERTICAL SLICE THEORIES ===
    "347_resonance": {
        "name": "The 347 Resonance",
        "category": "Conspiracy",
        "description": "347 isn't just a population count. It's a frequency. A threshold. A number that means something to whatever watches from the aurora.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Pattern Recognition": 3,
            "Occult Knowledge": 2,
            "Composure": -2
        },
        "conflicts_with": [],
        "auto_locks": [],
        "degradation_rate": 12,
        "internalize_time_hours": 10,
        "active_case": True,
        "critical_for_endgame": True
    },
    "aurora_rules": {
        "name": "The Aurora Has Rules",
        "category": "Belief",
        "description": "The lights follow patterns. Don't whistle. Don't wave. Don't count them. The old warnings aren't superstition—they're survival.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Paranormal Sensitivity": 2,
            "Survival": 2,
            "Skepticism": -2,
            "Logic": -1
        },
        "conflicts_with": ["there_is_a_rational_explanation"],
        "auto_locks": [],
        "degradation_rate": 10,
        "internalize_time_hours": 8,
        "active_case": True,
        "critical_for_endgame": True
    },
    "government_coverup": {
        "name": "Government Cover-Up",
        "category": "Conspiracy",
        "description": "The DEW line wasn't just watching for bombers. They knew about the lights. They've known for decades. And they're still here.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Research": 2,
            "Technology": 2,
            "Skepticism": 1,
            "Authority": -2
        },
        "conflicts_with": [],
        "auto_locks": [],
        "degradation_rate": 15,
        "internalize_time_hours": 6,
        "active_case": True,
        "critical_for_endgame": False
    },
    "something_watches": {
        "name": "Something Watches",
        "category": "Haunted",
        "description": "You can feel it. Eyes from everywhere and nowhere. The attention of something vast and patient.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Paranormal Sensitivity": 3,
            "Perception": 2,
            "Composure": -3,
            "Sanity Drain": 1
        },
        "conflicts_with": [],
        "auto_locks": [],
        "degradation_rate": 20,
        "internalize_time_hours": 4,
        "active_case": False,
        "critical_for_endgame": True
    },
    "ive_been_here_before": {
        "name": "I've Been Here Before",
        "category": "Haunted",
        "description": "This isn't your first time in Kaltvik. You've walked these streets. You've seen these faces. You just can't remember when.",
        "status": "locked",
        "hidden_effects": True,
        "effects": {
            "Pattern Recognition": 2,
            "Instinct": 2,
            "Composure": -2,
            "Logic": -1
        },
        "conflicts_with": [],
        "auto_locks": [],
        "degradation_rate": 25,
        "internalize_time_hours": 6,
        "active_case": False,
        "critical_for_endgame": True
    }
}
