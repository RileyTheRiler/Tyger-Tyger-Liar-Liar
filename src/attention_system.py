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
            },
            # New Triggers
            "read_redacted": {
                "cost": 15,
                "description": "You read words that were never meant to be seen. The page feels warm."
            },
            "discuss_forbidden": {
                "cost": 10,
                "description": "You speak of forbidden things. The shadows lean closer."
            },
            "curfew_violation": {
                "cost": 10, # Per hour (handled by caller logic usually)
                "description": "You are out past curfew. The Entity watches the empty streets."
            },
            "intuition_sacred": {
                "cost": 20,
                "description": "You open your mind in a sacred place. Something else floods in."
            },
            "internalize_theory": {
                "cost": 5,
                "description": "As the theory takes root in your mind, you feel a connection snap into place."
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
    
    print("\n[TEST 3] Reading redacted files...")
    result = attention.perform_taboo("read_redacted")
    print(f"  {result['action_description']}")
    print(f"  Attention gained: +{result['attention_gained']}")
    print(f"  Current level: {result['current_level']}%")

    print("\n[TEST 4] Making eye contact...")
    result = attention.perform_taboo("make_eye_contact")
    print(f"  {result['action_description']}")
    print(f"  Current level: {result['current_level']}%")
    print(f"  Warning: {result.get('warning')}")
    print(f"  Threshold crossed: {result['threshold_crossed']}")
    print(f"  {attention.get_status_display()}")
    
    # Test 5: Decay
    print("\n[TEST 5] Laying low for 10 hours...")
    attention.decay_attention(10)
    print(f"  Current level: {attention.attention_level}%")
    print(f"  {attention.get_status_display()}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_attention()
