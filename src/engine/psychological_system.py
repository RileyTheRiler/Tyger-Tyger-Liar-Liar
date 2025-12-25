"""
Psychological State System - Week 15
Manages Sanity, Mental Load, Fear Level, and psychological effects.
"""

import random
from typing import Dict, List, Tuple, Optional


class PsychologicalState:
    """
    Manages the player's psychological state including Sanity, Mental Load, 
    Fear Level, and derived states like Disorientation and Instability.
    """
    
    def __init__(self, player_state: dict):
        """
        Initialize psychological state manager.
        
        Args:
            player_state: Reference to the game's player_state dict
        """
        self.player_state = player_state
        
        # Initialize new psychological variables if not present
        if "mental_load" not in self.player_state:
            self.player_state["mental_load"] = 0
        if "fear_level" not in self.player_state:
            self.player_state["fear_level"] = 0
        if "disorientation" not in self.player_state:
            self.player_state["disorientation"] = False
        if "instability" not in self.player_state:
            self.player_state["instability"] = False
        if "hallucination_history" not in self.player_state:
            self.player_state["hallucination_history"] = []
    
    # ==================== SANITY SYSTEM ====================
    
    def get_sanity_tier(self) -> int:
        """
        Get the current sanity tier (0-4).
        
        Returns:
            0: 0 (breakdown)
            1: 1-24 (psychosis)
            2: 25-49 (hysteria)
            3: 50-74 (unsettled)
            4: 75-100 (stable)
        """
        sanity = self.player_state.get("sanity", 100.0)
        
        if sanity <= 0:
            return 0
        elif sanity < 25:
            return 1
        elif sanity < 50:
            return 2
        elif sanity < 75:
            return 3
        else:
            return 4
    
    def get_sanity_tier_name(self) -> str:
        """Get the descriptive name of the current sanity tier."""
        tier = self.get_sanity_tier()
        names = {
            0: "BREAKDOWN",
            1: "PSYCHOSIS",
            2: "HYSTERIA",
            3: "UNSETTLED",
            4: "STABLE"
        }
        return names.get(tier, "UNKNOWN")
    
    def modify_sanity(self, amount: float, reason: str = "Unknown") -> Dict:
        """
        Modify sanity and return effects triggered.
        
        Args:
            amount: Amount to change sanity by (negative = loss)
            reason: Description of what caused the change
            
        Returns:
            Dict with 'messages' and 'effects' keys
        """
        old_sanity = self.player_state["sanity"]
        old_tier = self.get_sanity_tier()
        
        self.player_state["sanity"] = max(0, min(100, old_sanity + amount))
        new_sanity = self.player_state["sanity"]
        new_tier = self.get_sanity_tier()
        
        result = {
            "messages": [],
            "effects": [],
            "tier_changed": old_tier != new_tier
        }
        
        # Log the change
        if amount != 0:
            sign = "+" if amount > 0 else ""
            result["messages"].append(f"[SANITY {sign}{amount:.0f}] {reason}")
        
        # Check for tier transitions
        if new_tier < old_tier:
            result["messages"].append(f"[PSYCHOLOGICAL STATE: {self.get_sanity_tier_name()}]")
            result["effects"].append(("tier_drop", new_tier))
            
            # Trigger tier-specific effects
            if new_tier == 0:
                result["effects"].append(("breakdown", None))
            elif new_tier == 1:
                result["effects"].append(("visual_hallucinations_enabled", True))
                self.player_state["instability"] = True
            elif new_tier == 2:
                result["effects"].append(("auditory_hallucinations_enabled", True))
        
        return result
    
    def get_mental_load_multiplier(self) -> float:
        """
        Get the Mental Load accumulation multiplier based on sanity tier.
        
        Returns:
            Multiplier (1.0 = normal, 1.5 = increased, etc.)
        """
        tier = self.get_sanity_tier()
        
        if tier >= 3:  # 50-100: Normal
            return 1.0
        elif tier == 2:  # 25-49: Increased
            return 1.5
        elif tier == 1:  # 1-24: Severe
            return 2.0
        else:  # 0: Critical
            return 3.0
    
    def should_skill_misfire(self) -> bool:
        """
        Check if a skill check should misfire due to low sanity.
        
        Returns:
            True if skill should misfire (49-25 range: 10% chance)
        """
        tier = self.get_sanity_tier()
        
        if tier == 2:  # 25-49 range
            return random.random() < 0.10
        elif tier == 1:  # 1-24 range
            return random.random() < 0.20
        
        return False
    
    # ==================== MENTAL LOAD SYSTEM ====================
    
    def add_mental_load(self, amount: int, source: str = "Unknown") -> Dict:
        """
        Add Mental Load with sanity-based multiplier.
        
        Args:
            amount: Base amount to add
            source: What caused the load
            
        Returns:
            Dict with messages and current load level
        """
        multiplier = self.get_mental_load_multiplier()
        actual_amount = int(amount * multiplier)
        
        old_load = self.player_state["mental_load"]
        self.player_state["mental_load"] = min(100, old_load + actual_amount)
        new_load = self.player_state["mental_load"]
        
        result = {
            "messages": [],
            "load_level": self.get_mental_load_level(),
            "amount_added": actual_amount
        }
        
        if actual_amount > 0:
            result["messages"].append(f"[MENTAL LOAD +{actual_amount}] {source}")
            
            # Check for threshold crossings
            if old_load < 50 <= new_load:
                result["messages"].append("[MENTAL LOAD: MODERATE] Your thoughts feel heavier.")
            elif old_load < 75 <= new_load:
                result["messages"].append("[MENTAL LOAD: HIGH] Concentration is becoming difficult.")
                self.player_state["disorientation"] = True
            elif old_load < 90 <= new_load:
                result["messages"].append("[MENTAL LOAD: CRITICAL] Your mind is fracturing under the strain.")
                self.player_state["instability"] = True
        
        return result
    
    def reduce_mental_load(self, amount: int, source: str = "Recovery") -> Dict:
        """
        Reduce Mental Load.
        
        Args:
            amount: Amount to reduce
            source: What caused the reduction
            
        Returns:
            Dict with messages
        """
        old_load = self.player_state["mental_load"]
        self.player_state["mental_load"] = max(0, old_load - amount)
        new_load = self.player_state["mental_load"]
        
        result = {
            "messages": [],
            "load_level": self.get_mental_load_level()
        }
        
        if amount > 0:
            result["messages"].append(f"[MENTAL LOAD -{amount}] {source}")
            
            # Update flags based on new load
            if new_load < 75:
                self.player_state["disorientation"] = False
            if new_load < 90:
                self.player_state["instability"] = False
        
        return result
    
    def get_mental_load_level(self) -> str:
        """Get descriptive level of mental load."""
        load = self.player_state.get("mental_load", 0)
        
        if load < 25:
            return "LOW"
        elif load < 50:
            return "MODERATE"
        elif load < 75:
            return "HIGH"
        elif load < 90:
            return "SEVERE"
        else:
            return "CRITICAL"
    
    def get_mental_load_penalty(self) -> int:
        """
        Get skill check penalty based on Mental Load.
        
        Returns:
            Penalty to apply to skill checks (0 to -3)
        """
        load = self.player_state.get("mental_load", 0)
        
        if load < 50:
            return 0
        elif load < 75:
            return -1
        elif load < 90:
            return -2
        else:
            return -3
    
    # ==================== FEAR LEVEL SYSTEM ====================
    
    def add_fear(self, amount: int, source: str = "Unknown") -> Dict:
        """
        Add Fear Level (temporary spikes).
        
        Args:
            amount: Amount to add
            source: What caused the fear
            
        Returns:
            Dict with messages and effects
        """
        old_fear = self.player_state["fear_level"]
        self.player_state["fear_level"] = min(100, old_fear + amount)
        new_fear = self.player_state["fear_level"]
        
        result = {
            "messages": [],
            "effects": []
        }
        
        if amount > 0:
            result["messages"].append(f"[FEAR +{amount}] {source}")
            
            # High fear amplifies Mental Load
            if new_fear >= 50:
                load_increase = amount // 2
                load_result = self.add_mental_load(load_increase, "Fear-induced stress")
                result["messages"].extend(load_result["messages"])
        
        return result
    
    def decay_fear(self, minutes: int) -> Dict:
        """
        Decay fear level over time (5 points per 10 minutes).
        
        Args:
            minutes: Time passed
            
        Returns:
            Dict with messages if significant decay occurred
        """
        decay_amount = (minutes // 10) * 5
        
        if decay_amount > 0:
            old_fear = self.player_state["fear_level"]
            self.player_state["fear_level"] = max(0, old_fear - decay_amount)
            
            return {
                "messages": [f"[Your fear subsides slightly...]"] if old_fear > 0 else [],
                "amount_decayed": decay_amount
            }
        
        return {"messages": [], "amount_decayed": 0}
    
    # ==================== STATE QUERIES ====================
    
    def get_psychological_summary(self) -> str:
        """
        Get a formatted summary of the current psychological state.
        
        Returns:
            Multi-line string with current state
        """
        sanity = self.player_state.get("sanity", 100.0)
        mental_load = self.player_state.get("mental_load", 0)
        fear = self.player_state.get("fear_level", 0)
        disoriented = self.player_state.get("disorientation", False)
        unstable = self.player_state.get("instability", False)
        
        lines = [
            "=== PSYCHOLOGICAL STATE ===",
            f"Sanity: {sanity:.0f}/100 ({self.get_sanity_tier_name()})",
            f"Mental Load: {mental_load}/100 ({self.get_mental_load_level()})",
            f"Fear Level: {fear}/100",
            ""
        ]
        
        # Status flags
        if disoriented or unstable:
            lines.append("Status Effects:")
            if disoriented:
                lines.append("  • DISORIENTED - Perception may be unreliable")
            if unstable:
                lines.append("  • UNSTABLE - Internal voices competing")
        
        # Penalties
        penalty = self.get_mental_load_penalty()
        if penalty < 0:
            lines.append(f"\nSkill Check Penalty: {penalty}")
        
        lines.append("=" * 27)
        
        return "\n".join(lines)
    
    def is_hallucinating(self) -> bool:
        """Check if player should experience hallucinations."""
        tier = self.get_sanity_tier()
        return tier <= 2  # Sanity < 50
    
    def can_have_visual_hallucinations(self) -> bool:
        """Check if player can have visual hallucinations."""
        tier = self.get_sanity_tier()
        return tier <= 1  # Sanity < 25
    
    def can_have_auditory_hallucinations(self) -> bool:
        """Check if player can have auditory hallucinations."""
        tier = self.get_sanity_tier()
        return tier <= 2  # Sanity < 50
    
    def record_hallucination(self, hallucination_id: str):
        """Record that a hallucination has been shown to avoid repetition."""
        if hallucination_id not in self.player_state["hallucination_history"]:
            self.player_state["hallucination_history"].append(hallucination_id)
    
    def has_seen_hallucination(self, hallucination_id: str) -> bool:
        """Check if a specific hallucination has already been shown."""
        return hallucination_id in self.player_state.get("hallucination_history", [])
