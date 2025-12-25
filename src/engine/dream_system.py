"""
Dream System - Generates and manages dream sequences based on player stats.
"""

import random
from typing import Dict, List, Optional, Tuple

class DreamSystem:
    def __init__(self, skill_system, player_state: dict):
        self.skill_system = skill_system
        self.player_state = player_state
        self.last_dream = None

        # Dream content templates
        self.dream_symbols = {
            "water": "The rising tide consumes the town.",
            "fire": "The library burns, but the books do not turn to ash.",
            "forest": "The trees have eyes, and they are judging you.",
            "mirror": "You look into the mirror, but the reflection is not yours.",
            "static": "The sky is filled with white noise.",
            "void": "You are falling forever into a starless sky."
        }

        self.prophecies = [
            "The bridge will fall when the clock strikes three.",
            "He is lying about the key.",
            "Look beneath the floorboards in the shed.",
            "The aurora feeds on silence."
        ]

    def generate_dream(self) -> Dict:
        """
        Generates a dream sequence based on current stats.
        Returns a dict with 'description', 'clarity', 'type'.
        """
        subconscious = self.skill_system.get_skill_total("Subconscious")
        intuition = self.skill_system.get_skill_total("Intuition")
        reason = self.skill_system.get_skill_total("Logic") # Using Logic as proxy for Reason if Reason attr isn't a skill itself

        # High Reason suppresses dreams
        if reason > 6 and reason > subconscious + 2:
            return {
                "type": "suppressed",
                "description": "You sleep deeply, a dreamless void of black logic.",
                "clarity": 0
            }

        dream_content = []
        dream_type = "normal"
        clarity = 1

        # Core Symbolism
        symbol = random.choice(list(self.dream_symbols.keys()))
        base_desc = self.dream_symbols[symbol]
        dream_content.append(base_desc)

        # Subconscious Effect (Clarity)
        if subconscious >= 6:
            clarity = 3
            dream_content.append(f"You understand that the {symbol} represents your guilt.")
        elif subconscious >= 4:
            clarity = 2
            dream_content.append(f"The {symbol} feels significant, but you can't grasp why.")
        else:
            clarity = 1
            dream_content.append("It makes no sense.")

        # Intuition Effect (Prophecy)
        if intuition >= 6:
            prophecy = random.choice(self.prophecies)
            dream_content.append(f"A voice whispers: '{prophecy}'")
            dream_type = "prophetic"
        elif intuition >= 4:
            dream_content.append("You feel a premonition of danger.")

        # Sanity Influence (Nightmare)
        sanity = self.player_state.get("sanity", 100)
        if sanity < 50:
            dream_type = "nightmare"
            dream_content.append("suddenly, everything turns to blood and static.")

        full_text = " ".join(dream_content)

        dream_data = {
            "type": dream_type,
            "description": full_text,
            "clarity": clarity,
            "symbol": symbol,
            "timestamp": self.player_state.get("time_passed_minutes", 0) # simplified
        }

        self.last_dream = dream_data
        return dream_data

    def recall_dream(self) -> str:
        """Attempts to recall the last dream."""
        if not self.last_dream:
            return "You try to grasp at fading memories, but there is nothing there."

        # Check if already recalled
        if self.last_dream.get("recalled"):
            return f"You remember: {self.last_dream['description']}"

        # Skill check to recall details?
        # For now, just allow it if clarity is high enough or random chance
        clarity = self.last_dream["clarity"]
        roll = random.randint(1, 10)

        if roll + clarity > 5:
            self.last_dream["recalled"] = True
            return f"The memory floods back: {self.last_dream['description']}"
        else:
            return "The dream slips through your fingers like smoke."

    def write_down_vision(self) -> str:
        """Records the dream to journal/notes."""
        if not self.last_dream or not self.last_dream.get("recalled"):
            return "You need to recall a dream first."

        if self.last_dream.get("recorded"):
            return "You have already written this down."

        self.last_dream["recorded"] = True

        # Add to thoughts if list exists
        if "thoughts" in self.player_state:
             self.player_state["thoughts"].append(f"Dream: {self.last_dream['symbol']}")

        return "You hastily scribble the vision into your notebook before it fades."
