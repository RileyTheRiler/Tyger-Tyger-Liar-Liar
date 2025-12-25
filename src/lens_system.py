"""
Lens System - Dual Narration Engine.
Filters narrative text based on the player's dominant worldview.
"""

from typing import Optional, Dict

class LensSystem:
    def __init__(self, skill_system, board):
        self.skill_system = skill_system
        self.board = board
        self.locked = False # Permanent worldview commitment (endgame)
        self.current_lens = "neutral" # neutral, believer, skeptic
        
    def calculate_lens(self) -> str:
        """
        Determines the current lens based on skill levels, active theories, and mental state.

        Archetypes:
        - BELIEVER: High Paranormal/Instinct. Sees connections and entities.
        - SKEPTIC: High Logic/Skepticism. Sees rational explanations and hoaxes.
        - HAUNTED: High Sanity Loss / High Attention. Sees threat and impending doom.
        - BALANCED (Neutral): No strong bias.
        """
        if self.locked:
            return self.current_lens
            
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

        # 3. Calculate Haunted Score
        # Driven by Attention (external threat) and Sanity (internal resilience)
        # Assuming AttentionSystem is available via some reference,
        # but current init only takes skill_system and board.
        # We need to access AttentionSystem or PlayerState from somewhere.
        # For now, let's assume we can pass it or it's attached to Board (unlikely).
        # We'll need to modify __init__ or pass state to calculate_lens.
        # But keeping signature compatible for now, let's try to get it from board or assume external update.

        # Actually, let's update calculate_lens to accept optional state,
        # but since it's called by game.py, we should update the call site too or add a setter.

        # Since I can't easily change the signature without checking all call sites (only game.py calls it mostly),
        # I will check if I can access player state.
        # The Board object doesn't have player state usually.

        # WAIT: Game.py initializes LensSystem with (self.skill_system, self.board).
        # It calls calculate_lens() without arguments.
        # So I need to add state awareness to LensSystem.
        pass

    def update_state(self, attention_level: int, sanity: float):
        """Update tracking of dynamic state for Haunted calculation."""
        self.attention_level = attention_level
        self.sanity = sanity

    def calculate_lens(self) -> str:
        """
        Determines the current lens based on skill levels and active theories.
        Now includes HAUNTED calculation.
        """
        if self.locked:
            return self.current_lens
            
        # 1. Get base scores from skills
        believer_score = (
            self.skill_system.get_skill_total("Paranormal Sensitivity") +
            self.skill_system.get_skill_total("Instinct")
        )

        skeptic_score = (
            self.skill_system.get_skill_total("Logic") +
            self.skill_system.get_skill_total("Skepticism")
        )

        # 2. Add weight from active theories
        if hasattr(self.board, 'theories'):
            if self.board.theories.get("i_want_to_believe") and self.board.theories["i_want_to_believe"].status == "active":
                believer_score += 4

            if self.board.theories.get("there_is_a_rational_explanation") and self.board.theories["there_is_a_rational_explanation"].status == "active":
                skeptic_score += 4

        # 3. Check Haunted Trigger
        # If we have state data (updated via update_state)
        haunted = False
        if hasattr(self, 'attention_level') and hasattr(self, 'sanity'):
            # Haunted if Attention > 50 AND Sanity < 40
            # OR if Sanity < 20 (Critical Breakdown)
            if (self.attention_level > 50 and self.sanity < 50) or (self.sanity < 25):
                haunted = True

        if haunted:
            self.current_lens = "haunted"
            return self.current_lens

        # 4. Threshold check for Believer vs Skeptic
        diff = believer_score - skeptic_score
        
        if diff >= 3:
            self.current_lens = "believer"
        elif diff <= -3:
            self.current_lens = "skeptic"
        else:
            self.current_lens = "balanced" # Renamed from neutral to align with GDD
            
        return self.current_lens

    def filter_text(self, base_text: str, variants: Optional[Dict[str, str]] = None) -> str:
        """
        Returns the appropriate text variant based on the current lens.
        variants: Dict like {"believer": "...", "skeptic": "...", "haunted": "..."}
        """
        lens = self.calculate_lens()
        
        if not variants:
            return base_text
            
        if lens in variants:
            return variants[lens]

        # Fallback logic
        if lens == "haunted":
            # Haunted might fall back to believer or base
            return variants.get("believer", base_text)
            
        return base_text

    def lock_lens(self, forced_lens: Optional[str] = None):
        """Permanently locks the current lens, typically for major story events."""
        if forced_lens:
            self.current_lens = forced_lens
        else:
            self.current_lens = self.calculate_lens()
        self.locked = True
        print(f"[SYSTEM] Worldview locked: {self.current_lens.upper()}")
