from typing import Dict, List, Optional, Any

class ManifestationManager:
    """
    Manages metaphysical triggers, specifically the '347 Rule' and other
    numerological resonances that attract the Entity.
    """
    
    def __init__(self, board_system, psychological_system, attention_system):
        self.board = board_system
        self.psych = psychological_system
        self.attention = attention_system
        
        # Cooldown prevents spamming manifestation events
        self.last_manifestation_time = 0
        self.cooldown_minutes = 60 

    def check_resonance(self, current_time_minutes: int) -> Dict[str, Any]:
        """
        Check for resonance patterns in the current game state.
        Returns a dict describing any triggered events.
        """
        if current_time_minutes - self.last_manifestation_time < self.cooldown_minutes:
            return {"triggered": False, "reason": "cooldown"}

        triggers = []
        
        # Rule 3: Active Theories
        active_theories_count = self.board.get_active_or_internalizing_count()
        
        # Rule 4: Sanity Tier (0-4)
        # We look for "Inverted 4" -> Tier 0 (Breakdown) or maybe specific Tier 4 alignment?
        # Let's use Sanity Tier.
        sanity_tier = self.psych.get_sanity_tier()
        
        # Rule 7: Friction or Insight
        # Using Friction Level / 10 roughly
        total_friction = self.board.get_total_friction()
        friction_factor = total_friction // 10
        
        # Check The 347 Rule
        # 3 Active Theories
        # 4 (Sanity Tier 4 = Stable, or maybe Tier 0 if we want "Inverted")
        # 7 (Friction/Load factor)
        
        # Interpretation: The Entity is attracted to ORDER imposed on CHAOS.
        # So 3 Theories (Order) + High Sanity (Order) + High Friction (Hidden Chaos) = Resonance.
        
        if active_theories_count >= 3 and sanity_tier == 4 and total_friction >= 70:
            triggers.append("347_resonance_major")
            
        # Minor Resonance: Just high friction and attention
        if total_friction > 50 and self.attention.attention_level > 50:
             triggers.append("friction_beacon")

        if not triggers:
             return {"triggered": False}

        # Execute Trigger
        event = self._execute_trigger(triggers[0], current_time_minutes)
        return event

    def _execute_trigger(self, trigger_type: str, time_now: int) -> Dict[str, Any]:
        self.last_manifestation_time = time_now
        
        if trigger_type == "347_resonance_major":
            # Massive attention spike + Reality Fracture
            self.attention.add_attention(34, "NUMEROLOGICAL RESONANCE (347)")
            self.psych.modify_sanity(-7, "The numbers align.")
            return {
                "triggered": True,
                "type": "manifestation",
                "message": "The stars align in a pattern of 3, 4, and 7. The Entity takes notice.",
                "force_scene": "reality_fracture_347" # Hypothetical scene
            }
            
        elif trigger_type == "friction_beacon":
            # Standard attraction
            self.attention.add_attention(10, "Cognitive Friction Beacon")
            return {
                "triggered": True,
                "type": "flavor",
                "message": "Your internal conflict acts as a beacon. The air grows colder."
            }
            
        return {"triggered": False}
