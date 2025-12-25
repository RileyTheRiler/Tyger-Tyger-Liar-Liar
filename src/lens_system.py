"""
Lens System - Triple Narration Engine.
Filters narrative text based on the player's dominant worldview.

Lenses:
- Believer: Sees supernatural significance in events
- Skeptic: Seeks rational explanations for everything
- Haunted: Filtered through memory, trauma, and past experience (NEW)
"""

from typing import Optional, Dict


class LensSystem:
    def __init__(self, skill_system, board, player_state=None, attention_system=None):
        self.skill_system = skill_system
        self.board = board
        self.player_state = player_state or {}
        self.attention_system = attention_system
        self.locked = False  # Permanent worldview commitment (endgame)
        self.current_lens = "neutral"  # neutral, believer, skeptic, haunted

        # Haunted lens triggers
        self.haunted_threshold_attention = 60  # Attention level that can trigger haunted
        self.haunted_threshold_sanity = 40  # Sanity below this increases haunted chance
        self.haunted_memory_weight = 3  # Weight per unlocked suppressed memory

    def calculate_lens(self) -> str:
        """
        Determines the current lens based on skill levels, active theories,
        attention level, and psychological state.

        Believer Skills: Paranormal Sensitivity, Instinct
        Skeptic Skills: Logic, Skepticism
        Haunted: Triggered by high attention, low sanity, or unlocked memories
        """
        if self.locked:
            return self.current_lens

        # 1. Calculate Haunted score first (can override other lenses)
        haunted_score = self._calculate_haunted_score()

        # If haunted score is very high, it takes over
        if haunted_score >= 10:
            self.current_lens = "haunted"
            return self.current_lens

        # 2. Get base scores from skills for believer/skeptic
        believer_score = (
            self.skill_system.get_skill_total("Paranormal Sensitivity") +
            self.skill_system.get_skill_total("Instinct")
        )

        skeptic_score = (
            self.skill_system.get_skill_total("Logic") +
            self.skill_system.get_skill_total("Skepticism")
        )

        # 3. Add weight from active theories
        if self.board.theories.get("i_want_to_believe") and self.board.theories["i_want_to_believe"].status == "active":
            believer_score += 4

        if self.board.theories.get("there_is_a_rational_explanation") and self.board.theories["there_is_a_rational_explanation"].status == "active":
            skeptic_score += 4

        # 4. Haunted can blend with other lenses at moderate levels
        # Add haunted weight to whichever lens is currently dominant
        if haunted_score >= 5:
            # Haunted state slightly biases toward believer (trauma opens the mind)
            believer_score += haunted_score // 2

        # 5. Threshold check
        diff = believer_score - skeptic_score

        if diff >= 3:
            self.current_lens = "believer"
        elif diff <= -3:
            self.current_lens = "skeptic"
        else:
            # At neutral, check if haunted should take over
            if haunted_score >= 7:
                self.current_lens = "haunted"
            else:
                self.current_lens = "neutral"

        return self.current_lens

    def _calculate_haunted_score(self) -> int:
        """
        Calculate the haunted score based on:
        - Attention level (high = more haunted)
        - Sanity (low = more haunted)
        - Reality (low = more haunted)
        - Unlocked suppressed memories
        - Active haunting theories
        """
        score = 0

        # Attention from the Entity
        if self.attention_system:
            attention = self.attention_system.attention_level
            if attention >= self.haunted_threshold_attention:
                score += (attention - self.haunted_threshold_attention) // 10

        # Low sanity increases haunted lens
        if self.player_state:
            sanity = self.player_state.get("sanity", 100)
            if sanity < self.haunted_threshold_sanity:
                score += (self.haunted_threshold_sanity - sanity) // 10

            reality = self.player_state.get("reality", 100)
            if reality < 50:
                score += (50 - reality) // 10

            # Each unlocked suppressed memory adds weight
            memories = self.player_state.get("suppressed_memories_unlocked", [])
            score += len(memories) * self.haunted_memory_weight

        # Certain theories trigger haunted lens
        haunted_theories = [
            "something_watches",
            "ive_been_here_before",
            "the_past_repeats",
            "memory_bleeds"
        ]
        for theory_id in haunted_theories:
            theory = self.board.theories.get(theory_id)
            if theory and theory.status == "active":
                score += 3

        return score

    def filter_text(self, base_text: str, variants: Optional[Dict[str, str]] = None) -> str:
        """
        Returns the appropriate text variant based on the current lens.
        variants: Dict like {"believer": "...", "skeptic": "...", "haunted": "..."}
        """
        lens = self.calculate_lens()

        if not variants:
            return base_text

        if lens == "believer" and "believer" in variants:
            return variants["believer"]
        elif lens == "skeptic" and "skeptic" in variants:
            return variants["skeptic"]
        elif lens == "haunted" and "haunted" in variants:
            return variants["haunted"]
        elif lens == "haunted" and "haunted" not in variants:
            # Fallback: if no haunted variant, apply haunted micro-overlay
            return self._apply_haunted_overlay(base_text)

        return base_text

    def _apply_haunted_overlay(self, text: str) -> str:
        """
        Apply subtle haunted modifications when no explicit haunted variant exists.
        Adds memory/deja-vu undertones to the text.
        """
        import random

        overlays = [
            "\n\n(You've seen this before. Haven't you?)",
            "\n\n(The memory of something similar tugs at your mind.)",
            "\n\n(This feels... familiar. Uncomfortably so.)",
            "\n\n(A fragment of something forgotten stirs.)",
            "\n\n(Was this a dream? Or a memory?)"
        ]

        # Only apply sometimes to avoid repetition
        if random.random() < 0.4:
            return text + random.choice(overlays)
        return text

    def lock_lens(self, forced_lens: Optional[str] = None):
        """Permanently locks the current lens, typically for major story events."""
        valid_lenses = ["believer", "skeptic", "haunted", "neutral"]
        if forced_lens and forced_lens in valid_lenses:
            self.current_lens = forced_lens
        else:
            self.current_lens = self.calculate_lens()
        self.locked = True
        print(f"[SYSTEM] Worldview locked: {self.current_lens.upper()}")

    def get_lens_description(self) -> str:
        """Get a human-readable description of the current lens state."""
        lens = self.calculate_lens()
        descriptions = {
            "neutral": "Your perception remains balanced, uncommitted.",
            "believer": "You see patterns, meaning, the supernatural lurking beneath.",
            "skeptic": "You seek rational explanations. There's always a logical answer.",
            "haunted": "The past bleeds into the present. Memories surface unbidden."
        }
        return descriptions.get(lens, "Your perception is unclear.")

    def set_player_state(self, player_state: dict):
        """Update the player state reference."""
        self.player_state = player_state

    def set_attention_system(self, attention_system):
        """Update the attention system reference."""
        self.attention_system = attention_system

    def to_dict(self) -> dict:
        """Serialize lens state for saving."""
        return {
            "locked": self.locked,
            "current_lens": self.current_lens
        }

    @classmethod
    def from_dict(cls, data: dict, skill_system, board, player_state=None, attention_system=None):
        """Restore lens state from saved data."""
        instance = cls(skill_system, board, player_state, attention_system)
        instance.locked = data.get("locked", False)
        instance.current_lens = data.get("current_lens", "neutral")
        return instance
