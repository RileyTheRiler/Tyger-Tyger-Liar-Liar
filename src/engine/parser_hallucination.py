"""
Parser Hallucination Engine - Week 15
Manages fake commands, ghost inputs, and hallucinated choices during low sanity.
"""

import random
from typing import List, Dict, Optional

class ParserHallucinationEngine:
    def __init__(self):
        self.active_hallucinations = []
        self.ghost_verbs = [
            "SCREAM", "RUN", "HIDE", "PRAY", "CONFESS", "DIE",
            "WAKE UP", "END IT", "SUBMIT", "OBEY", "LISTEN"
        ]

    def check_hallucination_trigger(self, sanity_tier: int) -> bool:
        """
        Check if a hallucination should trigger based on sanity.
        Tier 0 (Breakdown): 50% chance
        Tier 1 (Psychosis): 30% chance
        Tier 2 (Hysteria): 10% chance
        """
        chance = 0.0
        if sanity_tier == 0:
            chance = 0.5
        elif sanity_tier == 1:
            chance = 0.3
        elif sanity_tier == 2:
            chance = 0.1

        return random.random() < chance

    def generate_ghost_commands(self, count: int = 1, archetype: Optional[str] = None) -> List[str]:
        """Generate a list of hallucinated command suggestions."""
        verbs = list(self.ghost_verbs)
        if archetype == "skeptic":
            verbs += ["DEBUG", "REBOOT", "VERIFY", "LOG"]
        elif archetype == "believer":
            verbs += ["ASCEND", "OBSERVE", "BEHOLD", "REVEAL"]
            
        return random.sample(verbs, min(count, len(verbs)))

    def intercept_command(self, verb: str, target: str, archetype: Optional[str] = None) -> Optional[str]:
        """
        Potentially override a valid command with a hallucinated response.
        Returns the hallucinated response text if intercepted, else None.
        """
        if not verb: return None

        # Verb-specific hallucinations
        overrides = {
            "LOOK": [
                "You look, but only the abyss looks back.",
                "It's too bright. It burns.",
                "Don't look at it. Don't let it see you."
            ],
            "TAKE": [
                "It bites your hand!",
                "It's too heavy. It carries the weight of your sins.",
                "You reach out, but your hand passes through it like smoke."
            ],
            "TALK": [
                "Their mouth moves, but only static comes out.",
                "They know what you did.",
                "LIES. ALL LIES."
            ]
        }
        
        # Archetype specific overrides
        if archetype == "skeptic":
            overrides["VERIFY"] = ["ERROR: SOURCE UNRELIABLE", "Data corrupted by observer effect.", "Logic loop detected."]
        elif archetype == "believer":
            overrides["OBSERVE"] = ["The Pattern acknowledges you.", "It is blinding.", "The Sigil is complete."]

        if verb in overrides:
             return random.choice(overrides[verb])

        return None

    def get_hallucinated_choices(self, context_choices: List[Dict]) -> List[Dict]:
        """
        Inject hallucinated choices into the choice list.
        """
        fake_choices = [
            {"text": "SCREAM UNTIL YOUR LUNGS BLEED", "type": "hallucination"},
            {"text": "Tear out your eyes", "type": "hallucination"},
            {"text": "They are in the walls", "type": "hallucination"},
            {"text": "Admit your guilt", "type": "hallucination"},
            {"text": "The pattern is the key", "type": "hallucination"}
        ]

        num_to_add = random.randint(1, 3)
        return random.sample(fake_choices, num_to_add)
