"""
Psychological State System - Refactored
Manages Stress, Doubt, Obsession, Stability, and psychological effects.
"""

import random
from typing import Dict, List, Tuple, Optional


class PsychologicalState:
    """
    Manages the player's psychological state including Stability, Stress,
    Doubt, and Obsession.
    """
    
    def __init__(self, player_state: dict):
        """
        Initialize psychological state manager.
        
        Args:
            player_state: Reference to the game's player_state dict
        """
        self.player_state = player_state
        
        # Initialize new psychological variables if not present
        if "stress" not in self.player_state:
            # Map legacy mental_load if exists
            self.player_state["stress"] = self.player_state.get("mental_load", 0)

        if "doubt" not in self.player_state:
            self.player_state["doubt"] = 0

        if "obsession" not in self.player_state:
            self.player_state["obsession"] = 0

        if "stability" not in self.player_state:
            # Map legacy sanity if exists
            self.player_state["stability"] = self.player_state.get("sanity", 100.0)

        # Legacy flags
        if "disorientation" not in self.player_state:
            self.player_state["disorientation"] = False
        if "instability" not in self.player_state:
            self.player_state["instability"] = False
        if "hallucination_history" not in self.player_state:
            self.player_state["hallucination_history"] = []

    # ==================== STABILITY (Ex-Sanity) SYSTEM ====================
    
    @property
    def stability(self) -> float:
        return self.player_state["stability"]

    @stability.setter
    def stability(self, value: float):
        self.player_state["stability"] = max(0.0, min(100.0, value))
        # Sync legacy
        self.player_state["sanity"] = self.player_state["stability"]

    def get_stability_tier(self) -> int:
        """
        Get the current stability tier (0-4).
        """
        val = self.stability
        if val <= 0: return 0
        elif val < 25: return 1
        elif val < 50: return 2
        elif val < 75: return 3
        else: return 4
    
    def get_stability_description(self) -> str:
        """Get indirect symptom description of stability."""
        tier = self.get_stability_tier()
        descriptions = {
            0: "BROKEN",
            1: "FRACTURED",
            2: "SHAKING",
            3: "UNSETTLED",
            4: "FOCUSED"
        }
        return descriptions.get(tier, "UNKNOWN")
    
    def modify_stability(self, amount: float, reason: str = "Unknown") -> Dict:
        """Modify stability (sanity)."""
        old_tier = self.get_stability_tier()
        self.stability += amount
        new_tier = self.get_stability_tier()
        
        result = {
            "messages": [],
            "effects": []
        }
        
        if amount != 0:
            # Indirect feedback
            msg = "You feel your grip tightening." if amount > 0 else "You feel a piece of yourself slip away."
            result["messages"].append(f"[{msg}] ({reason})")

        if new_tier < old_tier:
            result["messages"].append(f"[MENTAL STATE: {self.get_stability_description()}]")
            if new_tier <= 1:
                result["effects"].append(("visual_hallucinations_enabled", True))
        
        return result

    # ==================== STRESS (Ex-Mental Load) SYSTEM ====================

    @property
    def stress(self) -> int:
        return self.player_state["stress"]

    @stress.setter
    def stress(self, value: int):
        self.player_state["stress"] = max(0, min(100, value))
        # Sync legacy
        self.player_state["mental_load"] = self.player_state["stress"]

    def add_stress(self, amount: int, source: str = "Unknown") -> Dict:
        """Add Stress."""
        self.stress += amount
        result = {"messages": []}
        
        if amount > 0:
            # Indirect feedback
            symptoms = [
                "Your temples throb.",
                "Your heart rate spikes.",
                "Gritting your teeth.",
                "A sharp migraine pierces your skull."
            ]
            symptom = symptoms[min(len(symptoms)-1, int(self.stress / 25))]
            result["messages"].append(f"[{symptom}]")
            
        return result

    def relieve_stress(self, amount: int, source: str = "Relief") -> Dict:
        """Relieve Stress."""
        self.stress -= amount
        return {"messages": ["You take a deep breath. The pressure subsides."]}

    def get_stress_symptom(self) -> str:
        if self.stress < 25: return "Calm"
        elif self.stress < 50: return "Tense"
        elif self.stress < 75: return "Strained"
        else: return "Overloaded"

    # ==================== DOUBT SYSTEM ====================

    @property
    def doubt(self) -> int:
        return self.player_state["doubt"]

    @doubt.setter
    def doubt(self, value: int):
        self.player_state["doubt"] = max(0, min(100, value))

    def add_doubt(self, amount: int, source: str = "Unknown") -> Dict:
        self.doubt += amount
        result = {"messages": []}
        if amount > 0 and self.doubt > 50:
            result["messages"].append("[Are you sure about that?]")
        return result

    def get_doubt_symptom(self) -> str:
        if self.doubt < 30: return "Confident"
        elif self.doubt < 60: return "Uncertain"
        else: return "Paranoid"

    # ==================== OBSESSION SYSTEM ====================

    @property
    def obsession(self) -> int:
        return self.player_state["obsession"]

    @obsession.setter
    def obsession(self, value: int):
        self.player_state["obsession"] = max(0, min(100, value))

    def add_obsession(self, amount: int, source: str = "Unknown") -> Dict:
        self.obsession += amount
        result = {"messages": []}
        if amount > 0 and self.obsession > 60:
             result["messages"].append("[You can't stop thinking about it.]")
        return result

    def get_obsession_symptom(self) -> str:
        if self.obsession < 30: return "Detached"
        elif self.obsession < 60: return "Fixated"
        else: return "Obsessed"

    # ==================== EFFECTS & THRESHOLDS ====================

    def should_trigger_text_distortion(self) -> bool:
        """
        Triggered by High Stress (>50) or Low Stability (<40).
        """
        return self.stress > 50 or self.stability < 40

    def should_trigger_hallucinated_options(self) -> bool:
        """
        Triggered by High Obsession (>50) or Very Low Stability (<25).
        """
        return self.obsession > 50 or self.stability < 25

    def should_trigger_missing_facts(self) -> bool:
        """
        Triggered by High Doubt (>50).
        """
        return self.doubt > 50

    def get_psychological_summary(self) -> str:
        return (
            "=== MENTAL STATE ===\n"
            f"Stability: {self.get_stability_description()} ({self.stability:.0f}%)\n"
            f"Stress:    {self.get_stress_symptom()} ({self.stress}%)\n"
            f"Doubt:     {self.get_doubt_symptom()} ({self.doubt}%)\n"
            f"Obsession: {self.get_obsession_symptom()} ({self.obsession}%)\n"
            "===================="
        )
    
    # Legacy / Compatibility methods
    def get_sanity_tier(self) -> int: return self.get_stability_tier()
    def is_hallucinating(self) -> bool: return self.stability < 50
    def decay_fear(self, minutes): return {"messages": []} # Stub for compatibility
    def to_dict(self): return {}
    def restore_state(self, state): pass
