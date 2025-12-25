from typing import Tuple, Optional
from tyger_game.engine.character import Character
from tyger_game.utils.constants import ALIGNMENTS

class AlignmentSystem:
    THRESHOLD_INITIATION = 4

    @staticmethod
    def modify_alignment(character: Character, axis: str, amount: int = 1) -> Optional[str]:
        """
        Increments an alignment score and checks for Initiation thresholds.
        axis: 'believer', 'skeptic', 'order', 'chaos'
        Returns: Name of alignment if a threshold is JUST crossed, else None.
        """
        if axis not in character.alignment_scores:
            raise ValueError(f"Invalid alignment axis: {axis}")
        
        old_val = character.alignment_scores[axis]
        character.alignment_scores[axis] += amount
        new_val = character.alignment_scores[axis]

        # Check for Initiation Threshold (The "Threshold of Four")
        if old_val < AlignmentSystem.THRESHOLD_INITIATION and new_val >= AlignmentSystem.THRESHOLD_INITIATION:
            # Trigger Vision Quest / Invitation
            return AlignmentSystem._get_potential_archetype(axis)
        
        # Re-evaluate dominant archetype
        character.active_alignment = AlignmentSystem.calculate_archetype(character)
        return None

    @staticmethod
    def calculate_archetype(character: Character) -> str:
        """Determines the current Epistemological Alignment."""
        scores = character.alignment_scores
        
        # Determine dominant poles
        belief_sc = scores['believer']
        skeptic_sc = scores['skeptic']
        order_sc = scores['order']
        chaos_sc = scores['chaos']

        # Simple dominance logic
        is_believer = belief_sc >= skeptic_sc
        is_order = order_sc >= chaos_sc

        if is_believer and is_order:
            return ALIGNMENTS["FUNDAMENTALIST"]
        elif is_believer and not is_order:
            return ALIGNMENTS["TRUTH_SEEKER"]
        elif not is_believer and is_order:
            return ALIGNMENTS["DEBUNKER"]
        else: # Skeptic + Chaos
            return ALIGNMENTS["OPPORTUNIST"]

    @staticmethod
    def _get_potential_archetype(trigger_axis: str) -> str:
        """Returns the localized name of the path associated with this axis."""
        # This is for the narrative hook: "You are leaning towards..."
        mapping = {
            "believer": "The Path of Gnosis",
            "skeptic": "The Path of Method",
            "order": "The Path of the Institution",
            "chaos": "The Path of the Iconoclast"
        }
        return mapping.get(trigger_axis, "Unknown Path")
