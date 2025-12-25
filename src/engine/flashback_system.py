import copy
from typing import Dict, Any, Optional, List

class FlashbackManager:
    """
    Manages POV (Point of View) shifts during flashback scenes.
    Temporarily swaps character stats and tracks unreliable narration.
    """
    def __init__(self, skill_system, player_state):
        self.skill_system = skill_system
        self.player_state = player_state
        self.original_stats = None
        self.original_archetype = None
        self.in_flashback = False
        self.current_pov_name = None

    def enter_flashback(self, pov_data: Dict[str, Any]):
        """
        Enters a flashback by storing current stats and applying POV stats.
        pov_data: {
            "name": "Captain Miller",
            "skills": {"Logic": 2, "Survival": 5, ...},
            "archetype": "SOLDIER"
        }
        """
        if self.in_flashback:
            return  # Already in a flashback

        self.in_flashback = True
        self.current_pov_name = pov_data.get("name", "Unknown POV")
        
        # Store original state
        self.original_stats = copy.deepcopy(self.skill_system.to_dict())
        self.original_archetype = self.player_state.get("archetype")

        # Apply POV stats
        self.skill_system.apply_temporary_pov(pov_data.get("skills", {}))
        if "archetype" in pov_data:
            self.player_state["archetype"] = pov_data["archetype"]

        print(f"[FLASHBACK] Entering POV: {self.current_pov_name}")

    def exit_flashback(self):
        """Restores original character state."""
        if not self.in_flashback:
            return

        # Restore from original_stats
        self.skill_system.load_state_from_dict(self.original_stats)
        self.player_state["archetype"] = self.original_archetype
        
        print(f"[FLASHBACK] Exited POV. Original state restored.")
        
        self.in_flashback = False
        self.original_stats = None
        self.original_archetype = None
        self.current_pov_name = None

    def get_memory_text(self, memory_data: Dict[str, Any]) -> str:
        """
        Retrieves the appropriate memory text based on current sanity.
        Supports 'objective' (High Sanity) vs 'traumatic' (Low Sanity) variants.
        """
        text_data = memory_data.get("text")
        
        # If text is just a string, return it (backward compatibility)
        if isinstance(text_data, str):
            return text_data
            
        # If it's a dictionary, select based on sanity
        if isinstance(text_data, dict):
            sanity = self.player_state.get("sanity", 100)
            # Tier 0-2 (Breakdown/Psychosis/Hysteria) -> Traumatic (< 50 sanity)
            # Tier 3-4 (Unsettled/Stable) -> Objective (>= 50 sanity)
            
            if sanity < 50:
                return text_data.get("traumatic", text_data.get("objective", "Memory corrupted."))
            else:
                return text_data.get("objective", text_data.get("traumatic", "Memory unavailable."))
                
        return "[MEMORY ERROR: INVALID DATA FORMAT]"

    def check_unreliable_narrator(self, text: str, context: Dict[str, Any]) -> str:
        """
        If Skepticism is high, highlights potential contradictions in the flashback.
        """
        if not self.in_flashback:
            return text

        skepticism = self.skill_system.get_skill("Skepticism").effective_level
        
        # Contradictions are marked in scene data like: [!! This doesn't match the reports !!]
        # or tagged via metadata. For now, we'll look for [!] marker.
        if skepticism >= 4 and "[!]" in text:
            highlighted = text.replace("[!]", "\n[UNRELIABLE NARRATOR: Your Skepticism detects a contradiction in this memory!]\n")
            return highlighted
            
        return text.replace("[!]", "") # Hide marker if skill low
