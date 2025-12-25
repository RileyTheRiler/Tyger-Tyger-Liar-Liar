import math
import random
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum

class SanityState(Enum):
    CLEAR = "Clear-headed"    # 80-100
    DISTRACTED = "Distracted" # 60-79
    UNSTABLE = "Unstable"     # 40-59
    PARANOID = "Paranoid"     # 20-39
    FRACTURED = "Fractured"   # 0-19

@dataclass
class ParanoiaVector:
    magnitude: float = 0.0
    direction: float = 0.0 # 0-360 degrees, just conceptual for now

    def increase(self, amount: float):
        self.magnitude = min(100.0, self.magnitude + amount)

    def decrease(self, amount: float):
        self.magnitude = max(0.0, self.magnitude - amount)

class PsychologicalSystem:
    def __init__(self, player_state: dict):
        self.player_state = player_state
        if "sanity" not in self.player_state:
            self.player_state["sanity"] = 100.0

        if "paranoia" not in self.player_state:
            self.player_state["paranoia"] = {"magnitude": 0.0, "direction": 0.0}

        if "hallucination_flags" not in self.player_state:
            self.player_state["hallucination_flags"] = set()

        self.paranoia_vector = ParanoiaVector(
            magnitude=self.player_state["paranoia"].get("magnitude", 0.0),
            direction=self.player_state["paranoia"].get("direction", 0.0)
        )

    def get_sanity(self) -> float:
        return self.player_state.get("sanity", 100.0)

    def set_sanity(self, value: float):
        self.player_state["sanity"] = max(0.0, min(100.0, float(value)))

    def modify_sanity(self, amount: float) -> str:
        old_state = self.get_sanity_state()
        self.set_sanity(self.get_sanity() + amount)
        new_state = self.get_sanity_state()

        msg = f"[SANITY {'+' if amount > 0 else ''}{amount}]"
        if old_state != new_state:
            msg += f" -> Mental State: {new_state.value.upper()}"
        return msg

    def get_sanity_state(self) -> SanityState:
        s = self.get_sanity()
        if s >= 80: return SanityState.CLEAR
        if s >= 60: return SanityState.DISTRACTED
        if s >= 40: return SanityState.UNSTABLE
        if s >= 20: return SanityState.PARANOID
        return SanityState.FRACTURED

    def get_clarity_index(self) -> str:
        """Abstracts sanity for the UI"""
        s = self.get_sanity()
        if s >= 90: return "Lucid"
        if s >= 70: return "Clouded"
        if s >= 50: return "Fraying"
        if s >= 30: return "Critical"
        return "Lost"

    def update_paranoia(self, source: str, amount: float = 1.0):
        """
        Updates the paranoia vector.
        Sources: 'isolation', 'contradiction', 'suppression'
        """
        self.paranoia_vector.increase(amount)
        self.player_state["paranoia"]["magnitude"] = self.paranoia_vector.magnitude
        # Direction could be influenced by source type if we want to get fancy later

    def get_paranoia_level(self) -> float:
        return self.paranoia_vector.magnitude

    def check_hallucination_trigger(self, trigger_type: str) -> bool:
        """
        Determines if a hallucination should occur based on sanity/paranoia.
        trigger_type: 'narrative', 'visual', 'textual', 'npc'
        """
        sanity = self.get_sanity()
        paranoia = self.get_paranoia_level()

        # Base probability inversely proportional to sanity
        prob = (100 - sanity) / 100.0

        # Paranoia increases probability
        prob += (paranoia / 200.0)

        if trigger_type == 'narrative':
            # Only at lower sanity
            if sanity > 40: return False
            return random.random() < prob * 0.5

        elif trigger_type == 'visual':
            if sanity > 60: return False
            return random.random() < prob * 0.8

        elif trigger_type == 'textual':
            if sanity > 60: return False
            return random.random() < prob

        elif trigger_type == 'npc':
            if sanity > 40: return False
            return random.random() < prob * 0.6

        return False

    def get_text_distortion(self, text: str) -> str:
        """Applies glitch effects to text based on sanity."""
        sanity = self.get_sanity()
        if sanity >= 60:
            return text

        words = text.split()
        new_words = []

        glitch_map = {
            "is": ["was", "is not", "could be"],
            "you": ["they", "it", "we"],
            "see": ["feel", "hear", "imagine"],
            "door": ["maw", "exit", "trap"],
            "friend": ["liar", "spy", "stranger"],
            "truth": ["lie", "fabrication", "story"]
        }

        for word in words:
            clean = word.lower().strip('.,!?')
            if clean in glitch_map and random.random() < ((60 - sanity) / 100.0):
                sub = random.choice(glitch_map[clean])
                if word[0].isupper(): sub = sub.capitalize()
                new_words.append(sub)
            else:
                new_words.append(word)

        return " ".join(new_words)

    def apply_dissociation(self, board_state_divergence: float):
        """
        Tracks divergence between player's Board state and canonical truth markers.
        Updates sanity/paranoia based on divergence.
        """
        if board_state_divergence > 50:
            self.update_paranoia("dissociation", 5.0)
            if self.get_sanity() > 30:
                 self.modify_sanity(-2.0)
                 return "[DISSOCIATION] Your theory drifts too far from reality. The headache returns."
        return ""

    def perform_recovery_action(self, action_type: str) -> str:
        if action_type == "drink_water":
            self.modify_sanity(5)
            return " The cold water shocks your system. Focus returns."
        elif action_type == "grounding":
            self.modify_sanity(10)
            self.paranoia_vector.decrease(5)
            return " You recite the facts. Name. Date. Location. You are here."
        return ""
