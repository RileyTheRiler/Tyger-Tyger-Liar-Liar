"""
Integration Stages - Progressive Possession System.
Tracks the player's gradual assimilation by the Entity.
"""

from typing import Dict, List, Optional
import random

# Integration stage definitions
INTEGRATION_STAGES = {
    0: {
        "name": "Unaffected",
        "description": "You are yourself. For now.",
        "symptoms": []
    },
    1: {
        "name": "Watched",
        "description": "You feel eyes on you, even when alone.",
        "symptoms": ["occasional_memory_gaps"],
        "sanity_drain_per_hour": 1
    },
    2: {
        "name": "Touched",
        "description": "Your thoughts sometimes feel... not your own.",
        "symptoms": ["memory_gaps", "compulsive_behaviors"],
        "sanity_drain_per_hour": 2
    },
    3: {
        "name": "Compromised",
        "description": "The boundary between you and IT is blurring.",
        "symptoms": ["memory_gaps", "compulsions", "dialogue_restrictions"],
        "sanity_drain_per_hour": 3,
        "reality_drain_per_hour": 2
    },
    4: {
        "name": "Integrated",
        "description": "You are no longer you. You are US.",
        "symptoms": ["full_hive_mind"],
        "game_over": True
    }
}


class IntegrationSystem:
    """Manages progressive possession mechanics."""
    
    def __init__(self):
        self.current_stage = 0
        self.integration_progress = 0.0  # 0-100 within current stage
        self.last_memory_gap_time = 0
        self.compulsion_active = False
        self.compulsion_command = None
        self.restricted_dialogue_options = []
        
    def update_from_attention(self, attention_level: int):
        """
        Updates integration stage based on attention level.
        High attention accelerates integration.
        """
        if attention_level >= 80 and self.current_stage < 4:
            self.integration_progress += 5.0  # Fast progression when noticed
        elif attention_level >= 60:
            self.integration_progress += 2.0
        elif attention_level >= 40:
            self.integration_progress += 0.5
        
        # Check for stage advancement
        if self.integration_progress >= 100.0 and self.current_stage < 4:
            self.advance_stage()
    
    def advance_stage(self):
        """Advances to next integration stage."""
        self.current_stage += 1
        self.integration_progress = 0.0
        
        stage_data = INTEGRATION_STAGES[self.current_stage]
        
        return {
            "stage": self.current_stage,
            "name": stage_data["name"],
            "description": stage_data["description"],
            "game_over": stage_data.get("game_over", False)
        }
    
    def trigger_memory_gap(self, current_time: float) -> Optional[Dict]:
        """
        Randomly triggers memory gaps (time skips).
        Returns dict with time lost if triggered.
        """
        if self.current_stage < 1:
            return None
        
        # Chance increases with stage
        chance = self.current_stage * 0.15  # 15% per stage
        
        if random.random() < chance:
            # Time lost increases with stage
            hours_lost = random.randint(1, self.current_stage * 2)
            
            return {
                "triggered": True,
                "hours_lost": hours_lost,
                "message": f"You blink. {hours_lost} hours have passed. You don't remember them."
            }
        
        return None
    
    def trigger_compulsion(self) -> Optional[Dict]:
        """
        Triggers compulsive behavior (forced command).
        Returns command player must execute.
        """
        if self.current_stage < 2:
            return None
        
        chance = (self.current_stage - 1) * 0.2  # 20% at stage 2, 40% at stage 3
        
        if random.random() < chance and not self.compulsion_active:
            compulsions = [
                {"command": "go north", "description": "You feel compelled to walk north."},
                {"command": "stare at aurora", "description": "You must look at the lights."},
                {"command": "whistle", "description": "A tune forms on your lips unbidden."},
                {"command": "wave", "description": "Your hand raises of its own accord."}
            ]
            
            compulsion = random.choice(compulsions)
            self.compulsion_active = True
            self.compulsion_command = compulsion["command"]
            
            return {
                "triggered": True,
                "command": compulsion["command"],
                "description": compulsion["description"]
            }
        
        return None
    
    def check_dialogue_restriction(self, dialogue_option: str) -> bool:
        """
        Checks if a dialogue option is restricted by integration.
        Returns True if option is allowed, False if restricted.
        """
        if self.current_stage < 3:
            return True
        
        # Stage 3: Some options become unavailable
        restricted_keywords = ["resist", "fight", "refuse", "no", "leave"]
        
        for keyword in restricted_keywords:
            if keyword in dialogue_option.lower():
                if random.random() < 0.6:  # 60% chance to be restricted
                    return False
        
        return True
    
    def get_stage_info(self) -> Dict:
        """Returns current stage information."""
        stage_data = INTEGRATION_STAGES[self.current_stage]
        
        return {
            "stage": self.current_stage,
            "name": stage_data["name"],
            "description": stage_data["description"],
            "progress": self.integration_progress,
            "symptoms": stage_data["symptoms"],
            "sanity_drain": stage_data.get("sanity_drain_per_hour", 0),
            "reality_drain": stage_data.get("reality_drain_per_hour", 0)
        }
    
    def get_status_display(self) -> str:
        """Returns formatted status for UI."""
        if self.current_stage == 0:
            return ""  # Hidden at stage 0
        
        stage_data = INTEGRATION_STAGES[self.current_stage]
        
        # Progress bar
        filled = int(self.integration_progress / 10)
        bar = "▓" * filled + "░" * (10 - filled)
        
        return f"[INTEGRATION: Stage {self.current_stage} - {stage_data['name']} {bar}]"
    
    def to_dict(self) -> Dict:
        """Serialize for save system."""
        return {
            "current_stage": self.current_stage,
            "integration_progress": self.integration_progress,
            "last_memory_gap_time": self.last_memory_gap_time,
            "compulsion_active": self.compulsion_active,
            "compulsion_command": self.compulsion_command,
            "restricted_dialogue_options": self.restricted_dialogue_options
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IntegrationSystem':
        """Deserialize from save data."""
        system = cls()
        system.current_stage = data.get("current_stage", 0)
        system.integration_progress = data.get("integration_progress", 0.0)
        system.last_memory_gap_time = data.get("last_memory_gap_time", 0)
        system.compulsion_active = data.get("compulsion_active", False)
        system.compulsion_command = data.get("compulsion_command")
        system.restricted_dialogue_options = data.get("restricted_dialogue_options", [])
        return system


def demo_integration():
    """Test integration system."""
    print("=" * 60)
    print("INTEGRATION SYSTEM DEMO")
    print("=" * 60)
    
    integration = IntegrationSystem()
    
    # Simulate high attention causing integration
    print("\n[Simulating high attention exposure...]")
    for i in range(25):
        integration.update_from_attention(85)
        if integration.integration_progress >= 100:
            result = integration.advance_stage()
            print(f"\n*** STAGE {result['stage']}: {result['name']} ***")
            print(f"    {result['description']}")
            if result.get('game_over'):
                print("    [GAME OVER]")
                break
    
    # Test memory gaps
    print("\n[Testing memory gaps...]")
    for _ in range(5):
        gap = integration.trigger_memory_gap(0)
        if gap:
            print(f"  {gap['message']}")
    
    # Test compulsions
    print("\n[Testing compulsions...]")
    for _ in range(5):
        comp = integration.trigger_compulsion()
        if comp:
            print(f"  {comp['description']}")
            print(f"  Must execute: '{comp['command']}'")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_integration()
