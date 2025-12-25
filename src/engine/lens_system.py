"""
Lens System - Dual Narration Engine.
Filters narrative text based on the player's dominant worldview.
"""

from typing import Optional, Dict
import logging

# Configure logger
logger = logging.getLogger(__name__)

class LensSystem:
    def __init__(self, skill_system, board, game_state=None):
        self.skill_system = skill_system
        self.board = board
        self.game_state = game_state
        self.locked = False # Permanent worldview commitment (endgame)
        self.current_lens = "neutral" # neutral, believer, skeptic, haunted
        
    def calculate_lens(self) -> str:
        """
        Determines the current lens based on skill levels and active theories.
        Believer Skills: Paranormal Sensitivity, Instinct
        Skeptic Skills: Logic, Skepticism
        Haunted Condition: Sanity < 40 or specific Trauma flags
        """
        if self.locked:
            return self.current_lens

        # 0. Check for Haunted (Overrides others if sanity is critical)
        # Assuming game_state is available, otherwise relying on external set
        if self.game_state and self.game_state.sanity < 40:
            self.current_lens = "haunted"
            return "haunted"
            
        # 1. Get base scores from skills
        # We use effective levels (including theory bonuses/penalties)
        believer_score = (
            self.skill_system.get_skill_total("Paranormal Sensitivity") +
            self.skill_system.get_skill_total("Instinct")
        )
        
        skeptic_score = (
            self.skill_system.get_skill_total("Logic") +
            self.skill_system.get_skill_total("Skepticism")
        )
        
        # 2. Add weight from active theories
        # Certain theories heavily bias the lens
        if self.board.theories.get("i_want_to_believe") and self.board.theories["i_want_to_believe"].status == "active":
            believer_score += 4
            
        if self.board.theories.get("there_is_a_rational_explanation") and self.board.theories["there_is_a_rational_explanation"].status == "active":
            skeptic_score += 4
            
        # 3. Threshold check
        # A significant lead (e.g., 3 points) is required to switch lens
        diff = believer_score - skeptic_score
        
        if diff >= 3:
            self.current_lens = "believer"
        elif diff <= -3:
            self.current_lens = "skeptic"
        else:
            self.current_lens = "neutral"
            
        return self.current_lens

    def resolve_text(self, archetype: str, stress_level: int, variants: Dict[str, str]) -> str:
        """
        Resolver function as requested.
        Inputs: archetype + stress level
        Output: selected text variant

        Also logs which text block fired.
        """
        selected_variant = None

        # Priority: Exact archetype match
        if archetype in variants:
            selected_variant = variants[archetype]
        elif "neutral" in variants:
             selected_variant = variants["neutral"]
        else:
            # Fallback to the first available or empty string
            selected_variant = next(iter(variants.values())) if variants else ""

        # Logging
        log_msg = f"[LENS RESOLVER] Archetype: {archetype}, Stress: {stress_level} -> Selected: '{selected_variant[:30]}...'"
        print(log_msg) # Printing to stdout as requested for visible debugging
        logger.debug(log_msg)

        return selected_variant

    def filter_text(self, base_text: str, variants: Optional[Dict[str, str]] = None) -> str:
        """
        Returns the appropriate text variant based on the current lens.
        variants: Dict like {"believer": "...", "skeptic": "..."}
        """
        lens = self.calculate_lens()
        
        if not variants:
            return base_text

        # Calculate stress level (proxy via game_state if available, else 0)
        stress = 0
        if self.game_state:
            stress = 100 - self.game_state.sanity
            
        return self.resolve_text(lens, stress, variants)

    def lock_lens(self, forced_lens: Optional[str] = None):
        """Permanently locks the current lens, typically for major story events."""
        if forced_lens:
            self.current_lens = forced_lens
        else:
            self.current_lens = self.calculate_lens()
        self.locked = True
        print(f"[SYSTEM] Worldview locked: {self.current_lens.upper()}")
