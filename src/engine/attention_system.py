"""
Attention System - Entity Awareness Tracker.
Gamifies indigenous taboos around the aurora.
"""

from typing import Dict, Optional, Tuple

class AttentionSystem:
    """Tracks how much the Entity is aware of the player."""
    
    def __init__(self):
        self.attention_level = 0  # 0-100
        self.decay_rate = 2  # Per hour of game time
        self.integration_threshold = 80  # When Integration begins
        self.discovered = False  # Has player learned about this mechanic?
        
        # Taboo actions and their attention costs
        self.taboo_actions = {
            "whistle_at_aurora": {
                "cost": 15,
                "description": "You whistle at the lights. They seem to... pause."
            },
            "sing_outdoors": {
                "cost": 10,
                "description": "Your voice carries into the night. The aurora ripples."
            },
            "wave_at_lights": {
                "cost": 12,
                "description": "You wave at the aurora. It waves back."
            },
            "photograph_aurora": {
                "cost": 8,
                "description": "The camera flash illuminates the sky. The lights descend slightly."
            },
            "speak_entity_name": {
                "cost": 20,
                "description": "You speak its name aloud. The temperature drops."
            },
            "make_eye_contact": {
                "cost": 25,
                "description": "You stare directly into the lights. They stare back."
            },
            "call_out": {
                "cost": 18,
                "description": "You shout into the darkness. Something hears you."
            },
            "dance": {
                "cost": 14,
                "description": "You dance beneath the aurora. It mirrors your movements."
            }
        }
        
        # Week 16: Non-taboo attention triggers
        self.other_triggers = {
            "use_surveillance_equipment": {
                "cost": 6,
                "description": "The camera feels heavier. The lens reflects something that wasn't there."
            },
            "use_em_detector": {
                "cost": 8,
                "description": "The EM detector screams. The readings make no sense."
            },
            "interrogate_integrated_npc": {
                "cost": 12,
                "description": "Their eyes go blank for a moment. You feel something watching through them."
            },
            "internalize_destabilizing_theory": {
                "cost": 10,
                "description": "The theory settles into your mind. Reality feels less stable."
            }
        }
    
    def perform_taboo(self, action_key: str) -> Dict:
        """
        Player performs a taboo action.
        Returns result with attention gained and warning message.
        """
        if action_key not in self.taboo_actions:
            return {
                "success": False,
                "message": "Unknown action."
            }
        
        action = self.taboo_actions[action_key]
        increase = action["cost"]
        
        self.attention_level = min(100, self.attention_level + increase)
        self.discovered = True  # Player now knows this mechanic exists
        
        return {
            "success": True,
            "action_description": action["description"],
            "attention_gained": increase,
            "current_level": self.attention_level,
            "warning": self._get_warning_message(),
            "threshold_crossed": self.attention_level >= self.integration_threshold
        }
    
    def add_attention(self, amount: int, reason: str = "") -> Dict:
        """
        Add attention for non-taboo reasons (equipment use, NPC interaction, etc.).
        Returns result with attention gained and current status.
        """
        old_level = self.attention_level
        self.attention_level = min(100, self.attention_level + amount)
        self.discovered = True
        
        # Check if we crossed the integration threshold
        threshold_crossed = (old_level < self.integration_threshold and 
                           self.attention_level >= self.integration_threshold)
        
        return {
            "success": True,
            "attention_gained": amount,
            "current_level": self.attention_level,
            "reason": reason,
            "warning": self._get_warning_message(),
            "threshold_crossed": threshold_crossed
        }
    
    def get_threshold_effects(self) -> Dict:
        """
        Returns active effects based on current attention level.
        These modify gameplay mechanics.
        """
        effects = {}
        
        if self.attention_level >= 26:  # 26-50: Minor interference
            effects["hallucination_chance"] = 0.05
            effects["signal_interference"] = True
            
        if self.attention_level >= 51:  # 51-75: Unexplained events
            effects["hallucination_chance"] = 0.15
            effects["item_displacement_chance"] = 0.1
            effects["npc_behavior_anomalies"] = True
            
        if self.attention_level >= 76:  # 76-99: Supernatural feedback
            effects["hallucination_chance"] = 0.30
            effects["item_displacement_chance"] = 0.25
            effects["time_distortion_chance"] = 0.15
            effects["reality_drain_per_hour"] = 2
            
        if self.attention_level >= 100:  # 100: Integration attempt
            effects["integration_attempt_pending"] = True
            effects["forced_event"] = "entity_manifestation"
        
        return effects
    
    def trigger_integration_attempt(self) -> Dict:
        """
        Called when attention reaches 100.
        Returns event data for integration attempt.
        """
        return {
            "triggered": True,
            "event_id": "entity_manifestation",
            "message": "The aurora descends. IT SEES YOU.",
            "force_scene": True
        }
    
    def decay_attention(self, hours: float):
        """Attention slowly decreases if player 'lays low'."""
        decay_amount = self.decay_rate * hours
        self.attention_level = max(0, self.attention_level - decay_amount)
    
    def _get_warning_message(self) -> Optional[str]:
        """Returns contextual warning based on attention level."""
        if self.attention_level < 30:
            return None
        elif self.attention_level < 60:
            return "The aurora seems... closer tonight."
        elif self.attention_level < 80:
            return "You feel watched. The hairs on your neck stand up."
        else:
            return "IT SEES YOU."
    
    def get_status_display(self) -> str:
        """Returns formatted status for UI display."""
        if not self.discovered:
            return ""  # Hidden until first taboo
        
        # Visual bar
        filled = int(self.attention_level / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        status = "SAFE"
        if self.attention_level >= 80:
            status = "CRITICAL"
        elif self.attention_level >= 60:
            status = "DANGEROUS"
        elif self.attention_level >= 30:
            status = "NOTICED"
        
        return f"[ATTENTION: {bar} {self.attention_level:.0f}% - {status}]"
    
    def to_dict(self) -> Dict:
        """Serialize for save system."""
        return {
            "attention_level": self.attention_level,
            "decay_rate": self.decay_rate,
            "integration_threshold": self.integration_threshold,
            "discovered": self.discovered
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttentionSystem':
        """Deserialize from save data."""
        system = cls()
        system.attention_level = data.get("attention_level", 0)
        system.decay_rate = data.get("decay_rate", 2)
        system.integration_threshold = data.get("integration_threshold", 80)
        system.discovered = data.get("discovered", False)
        return system


def demo_attention():
    """Test the attention system."""
    print("=" * 60)
    print("ATTENTION SYSTEM DEMO")
    print("=" * 60)
    
    attention = AttentionSystem()
    
    # Test 1: Perform taboo action
    print("\n[TEST 1] Whistling at aurora...")
    result = attention.perform_taboo("whistle_at_aurora")
    print(f"  {result['action_description']}")
    print(f"  Attention gained: +{result['attention_gained']}")
    print(f"  Current level: {result['current_level']}%")
    print(f"  Warning: {result.get('warning', 'None')}")
    print(f"  {attention.get_status_display()}")
    
    # Test 2: Multiple actions
    print("\n[TEST 2] Singing outdoors...")
    result = attention.perform_taboo("sing_outdoors")
    print(f"  Current level: {result['current_level']}%")
    print(f"  {attention.get_status_display()}")
    
    print("\n[TEST 3] Making eye contact...")
    result = attention.perform_taboo("make_eye_contact")
    print(f"  {result['action_description']}")
    print(f"  Current level: {result['current_level']}%")
    print(f"  Warning: {result.get('warning')}")
    print(f"  Threshold crossed: {result['threshold_crossed']}")
    print(f"  {attention.get_status_display()}")
    
    # Test 4: Decay
    print("\n[TEST 4] Laying low for 10 hours...")
    attention.decay_attention(10)
    print(f"  Current level: {attention.attention_level}%")
    print(f"  {attention.get_status_display()}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_attention()
