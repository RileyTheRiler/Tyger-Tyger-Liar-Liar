"""
Psychological State System - Week 15
Manages Sanity, Mental Load, Fear Level, and psychological effects.
Week 20 Update: Added Soft Failure States.
"""

import random
from typing import Dict, List, Tuple, Optional
from enum import Enum

class FailureType(Enum):
    NONE = "none"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    SOCIAL_BREAKDOWN = "social_breakdown"
    INVESTIGATIVE_PARALYSIS = "investigative_paralysis"

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
        if "active_failures" not in self.player_state:
            self.player_state["active_failures"] = []
        if "narrative_entropy" not in self.player_state:
            self.player_state["narrative_entropy"] = 0.0
    
    # ==================== SOFT FAILURE SYSTEM ====================

    def check_soft_failures(self, board_theory_count: int = 0) -> List[FailureType]:
        """
        Check for conditions triggering soft failure states.
        Returns list of newly triggered failures.
        """
        new_failures = []
        current_failures = set(self.player_state.get("active_failures", []))

        # 1. Cognitive Overload
        # Trigger: Mental Load >= 100
        if self.player_state["mental_load"] >= 100:
            if FailureType.COGNITIVE_OVERLOAD.value not in current_failures:
                self.trigger_failure(FailureType.COGNITIVE_OVERLOAD)
                new_failures.append(FailureType.COGNITIVE_OVERLOAD)

        # 2. Social Breakdown
        # Trigger: Fear Level >= 90 AND Sanity < 30
        if self.player_state["fear_level"] >= 90 and self.player_state["sanity"] < 30:
            if FailureType.SOCIAL_BREAKDOWN.value not in current_failures:
                self.trigger_failure(FailureType.SOCIAL_BREAKDOWN)
                new_failures.append(FailureType.SOCIAL_BREAKDOWN)

        # 3. Investigative Paralysis
        # Trigger: Reality < 10 OR (Active Theories > 5 AND Mental Load > 80)
        # Note: Active theories passed in as arg since board isn't stored here
        reality = self.player_state.get("reality", 100)
        load = self.player_state["mental_load"]

        if reality < 10 or (board_theory_count > 5 and load > 80):
            if FailureType.INVESTIGATIVE_PARALYSIS.value not in current_failures:
                self.trigger_failure(FailureType.INVESTIGATIVE_PARALYSIS)
                new_failures.append(FailureType.INVESTIGATIVE_PARALYSIS)

        return new_failures

    def trigger_failure(self, failure: FailureType):
        """Activate a soft failure state."""
        if "active_failures" not in self.player_state:
            self.player_state["active_failures"] = []

        if failure.value not in self.player_state["active_failures"]:
            self.player_state["active_failures"].append(failure.value)

            # Immediate effects?
            # We don't notify explicitly ("No explicit notification"), but effects apply
            pass

    def recover_from_failure(self, failure: FailureType) -> Dict:
        """
        Attempt to recover from a failure state.
        Applies permanent cost.
        """
        if "active_failures" not in self.player_state:
            return {"success": False, "message": "No active failures."}

        if failure.value in self.player_state["active_failures"]:
            self.player_state["active_failures"].remove(failure.value)

            # Permanent Cost
            cost_msg = ""
            if failure == FailureType.COGNITIVE_OVERLOAD:
                # Permanent max mental load reduction? Or just sanity hit?
                # Let's say: Permanent Scar
                if "scars" not in self.player_state: self.player_state["scars"] = []
                self.player_state["scars"].append("Frayed Nerves")
                cost_msg = "You feel permanently frayed."

            elif failure == FailureType.SOCIAL_BREAKDOWN:
                if "scars" not in self.player_state: self.player_state["scars"] = []
                self.player_state["scars"].append("Paranoid")
                cost_msg = "You can't trust anyone fully anymore."

            elif failure == FailureType.INVESTIGATIVE_PARALYSIS:
                if "scars" not in self.player_state: self.player_state["scars"] = []
                self.player_state["scars"].append("Hesitant")
                cost_msg = "You doubt your own conclusions."

            # Reset relevant stats to safe levels
            if failure == FailureType.COGNITIVE_OVERLOAD:
                self.player_state["mental_load"] = 50
            elif failure == FailureType.SOCIAL_BREAKDOWN:
                self.player_state["fear_level"] = 50
            elif failure == FailureType.INVESTIGATIVE_PARALYSIS:
                if self.player_state["reality"] < 20:
                    self.player_state["reality"] = 30

            return {
                "success": True,
                "message": f"You have recovered from {failure.value.replace('_', ' ')}. {cost_msg}"
            }

        return {"success": False, "message": "Failure state not active."}

    def is_failure_active(self, failure: FailureType) -> bool:
        return failure.value in self.player_state.get("active_failures", [])

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
                # Soft failure check happens in game loop, but we flag breakdown
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

    def modify_entropy(self, amount: float, reason: str = "Unstable thoughts") -> Dict:
        """
        Modify narrative entropy and return messages.
        Higher entropy represents a loosening grip on objective reality.
        """
        old_entropy = self.player_state.get("narrative_entropy", 0.0)
        self.player_state["narrative_entropy"] = max(0.0, min(100.0, old_entropy + amount))
        
        result = {
            "messages": [],
            "current": self.player_state["narrative_entropy"]
        }
        
        if amount != 0:
            sign = "+" if amount > 0 else ""
            result["messages"].append(f"[NARRATIVE ENTROPY {sign}{amount:.1f}] {reason}")
            
        return result
    
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
        active_failures = self.player_state.get("active_failures", [])
        
        lines = [
            "=== PSYCHOLOGICAL STATE ===",
            f"Sanity: {sanity:.0f}/100 ({self.get_sanity_tier_name()})",
            f"Mental Load: {mental_load}/100 ({self.get_mental_load_level()})",
            f"Fear Level: {fear}/100",
            ""
        ]
        
        # Status flags
        if disoriented or unstable or active_failures:
            lines.append("Status Effects:")
            if disoriented:
                lines.append("  • DISORIENTED - Perception may be unreliable")
            if unstable:
                lines.append("  • UNSTABLE - Internal voices competing")
            for af in active_failures:
                lines.append(f"  • {af.upper().replace('_', ' ')} - Functionality compromised")
        
        # Penalties
        penalty = self.get_mental_load_penalty()
        if penalty < 0:
            lines.append(f"\nSkill Check Penalty: {penalty}")
        
        lines.append("=" * 27)
        
        return "\n".join(lines)
    
    def is_hallucinating(self) -> bool:
        """Check if player should experience hallucinations."""
        tier = self.get_sanity_tier()
        # Also trigger if soft failures active
        active_failures = self.player_state.get("active_failures", [])
        return tier <= 2 or len(active_failures) > 0
    
    def can_have_visual_hallucinations(self) -> bool:
        """Check if player can have visual hallucinations."""
        tier = self.get_sanity_tier()
        active_failures = self.player_state.get("active_failures", [])
        return tier <= 1 or FailureType.COGNITIVE_OVERLOAD.value in active_failures
    
    def can_have_auditory_hallucinations(self) -> bool:
        """Check if player can have auditory hallucinations."""
        tier = self.get_sanity_tier()
        active_failures = self.player_state.get("active_failures", [])
        return tier <= 2 or FailureType.SOCIAL_BREAKDOWN.value in active_failures
    
    def record_hallucination(self, hallucination_id: str):
        """Record that a hallucination has been shown to avoid repetition."""
        if hallucination_id not in self.player_state["hallucination_history"]:
            self.player_state["hallucination_history"].append(hallucination_id)
    
    def has_seen_hallucination(self, hallucination_id: str) -> bool:
        """Check if a specific hallucination has already been shown."""
        return hallucination_id in self.player_state.get("hallucination_history", [])

    def to_dict(self) -> Dict:
        """Serialize psychological state (most data is in player_state, but for consistency)."""
        # Since this class wraps player_state, most data is already saved there.
        # This is provided if we need to save transient state not in player_state.
        return {}

    def restore_state(self, state: Dict):
        """Restore psychological state."""
        # Most data is in player_state, so this might be empty or used for future transient data.
        pass
