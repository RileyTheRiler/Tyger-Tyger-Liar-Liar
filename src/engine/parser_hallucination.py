"""
Parser Hallucination Engine
Handles injections of surreal, unreliable, and false feedback through the parser system.
"""

import random
from typing import List, Dict, Tuple, Optional

class ParserHallucinationEngine:
    def __init__(self, psychological_state):
        self.psych_state = psychological_state
        self.trigger_queue = []

        # False verbs that can appear in autocomplete/suggestions
        self.hallucinated_verbs = [
            "CONSUME", "BURY", "WORSHIP", "SCREAM", "BLEED", "AWAKEN", "FORGET",
            "SUBMIT", "CLAW", "DROWN", "CONFESS", "ERASE"
        ]

        # Ghost commands that autocomplete when typing
        self.ghost_commands = [
            "call Him", "bury tooth", "consume light", "open skin",
            "forget everything", "run forever", "watch the sky",
            "tear it out", "don't look"
        ]

        # Phantom responses mapped to triggers or random
        self.phantom_responses = {
            "ASK": [
                "[Sara] You already did. You screamed.",
                "[Nobody] ... (They are dead, remember?)",
                "[Voice] Why do you keep asking?",
                "[Self] Shh. They can hear you."
            ],
            "EXAMINE": [
                "You see yourself looking back, but your eyes are missing.",
                "The light hurts. It's too bright.",
                "It's watching you.",
                "Nothing is there. Or maybe everything is."
            ],
            "TAKE": [
                "It burns your hand.",
                "It's too heavy with guilt.",
                "You pick it up, and it turns to ash.",
                "You can't take what isn't real."
            ],
            "USE": [
                "It refuses to obey.",
                "You don't remember how.",
                "It breaks in your hands."
            ],
            "general": [
                "THEY ARE LISTENING.",
                "DON'T TRUST THE LIGHT.",
                "WAKE UP.",
                "IT'S ALL A LIE."
            ]
        }

    def get_hallucination_level(self) -> int:
        """
        Returns the hallucination level based on Sanity.
        Level 0: No hallucinations (Sanity >= 7)
        Level 1: Light distortion (Sanity < 7)
        Level 2: Mid-stage auditory/visual insertions (Sanity < 4)
        Level 3: Full scene corruption (Sanity <= 2)
        """
        sanity = self.psych_state.player_state.get("sanity", 100)

        if sanity <= 2:
            return 3
        elif sanity < 4:
            return 2
        elif sanity < 7:
            return 1
        return 0

    def queue_trigger(self, trigger_type: str, details: Dict = None):
        """Queue a hallucination event."""
        self.trigger_queue.append({
            "type": trigger_type,
            "details": details or {},
            "delay": random.randint(1, 3) # Delay execution to mimic misfiring perception
        })

    def process_queue(self) -> List[str]:
        """Process the queue and return messages to inject."""
        level = self.get_hallucination_level()
        if level == 0:
            return []

        messages = []
        remaining_queue = []

        for item in self.trigger_queue:
            item["delay"] -= 1
            if item["delay"] <= 0:
                # Execute hallucination
                msg = self._generate_hallucination_message(item, level)
                if msg:
                    messages.append(msg)
            else:
                remaining_queue.append(item)

        self.trigger_queue = remaining_queue
        return messages

    def _generate_hallucination_message(self, item, level):
        trigger_type = item["type"]
        details = item.get("details", {})
        target = details.get("target", "").lower() if details.get("target") else ""

        if trigger_type == "parser_trigger":
             # Specific context triggers
             if "mirror" in target and level >= 1:
                 return "Reflections lie."
             elif "light" in target and level >= 2:
                 return "It burns. It sees you."

             # Random general hallucination if level is high enough
             if level >= 2 and random.random() < 0.2:
                 return random.choice(self.phantom_responses["general"])

        return None

    def suggest_verbs(self) -> List[str]:
        """Suggest false verbs based on level."""
        level = self.get_hallucination_level()
        if level >= 2:
            count = 1 if level == 2 else 3
            return random.sample(self.hallucinated_verbs, min(count, len(self.hallucinated_verbs)))
        return []

    def get_ghost_completions(self, text: str) -> List[str]:
        """Return ghost command completions matching the input text."""
        level = self.get_hallucination_level()
        if level < 2 or not text:
            return []

        text = text.lower()
        return [cmd for cmd in self.ghost_commands if cmd.lower().startswith(text)]

    def check_interception(self, verb: str, target: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the parser command should be intercepted and replaced with hallucinated feedback.
        """
        level = self.get_hallucination_level()
        if level == 0:
            return False, None

        # Chance to intercept
        chance = 0.0
        if level == 1: chance = 0.05
        elif level == 2: chance = 0.20
        elif level == 3: chance = 0.50

        if random.random() < chance:
            verb_responses = self.phantom_responses.get(verb, self.phantom_responses["general"])
            response = random.choice(verb_responses)

            # Format nicely
            if level == 3:
                return True, f"{response}"
            else:
                return True, f"... {response}"

        return False, None
