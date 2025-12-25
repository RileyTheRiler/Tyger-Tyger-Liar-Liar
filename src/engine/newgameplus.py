import os
import json
from typing import Dict, Any, Optional, List

class NewGamePlusManager:
    """
    Manages New Game+ features including:
    - Previous save detection
    - Bonus theory unlocks
    - Starting skill point bonuses
    - Entity echo dialogue
    """
    def __init__(self, save_system):
        self.save_system = save_system
        self.ng_plus_active = False
        self.previous_data = None
        self.echo_dialogue_unlocked = False
        
    def check_eligibility(self) -> bool:
        """Checks if a completed save file exists."""
        saves = self.save_system.list_saves()
        for save in saves:
            # Check if any save has reached an ending
            save_data = self.save_system.load_game(save["slot"])
            if save_data and save_data.get("game_completed", False):
                return True
        return False
    
    def load_previous_playthrough(self) -> Optional[Dict[str, Any]]:
        """Loads data from the most recent completed playthrough."""
        saves = self.save_system.list_saves()
        completed_saves = []
        
        for save in saves:
            save_data = self.save_system.load_game(save["slot"])
            if save_data and save_data.get("game_completed", False):
                completed_saves.append({
                    "slot": save["slot"],
                    "timestamp": save.get("timestamp", 0),
                    "data": save_data
                })
        
        if not completed_saves:
            return None
            
        # Get most recent
        completed_saves.sort(key=lambda x: x["timestamp"], reverse=True)
        self.previous_data = completed_saves[0]["data"]
        return self.previous_data
    
    def activate_ng_plus(self, skill_system, board):
        """Applies NG+ bonuses to a new game."""
        if not self.previous_data:
            return False
            
        self.ng_plus_active = True
        
        # Grant bonus skill points
        skill_system.skill_points += 3
        print("[NEW GAME+] You start with +3 bonus skill points!")
        
        # Unlock bonus theories based on previous ending
        ending = self.previous_data.get("ending_type", "unknown")
        bonus_theories = self._get_bonus_theories(ending)
        
        for theory_id in bonus_theories:
            theory = board.get_theory(theory_id)
            if theory and theory.status == "locked":
                theory.status = "available"
                print(f"[NEW GAME+] Unlocked bonus theory: {theory.name}")
        
        # Enable echo dialogue
        self.echo_dialogue_unlocked = True
        
        return True
    
    def _get_bonus_theories(self, ending_type: str) -> List[str]:
        """Returns theory IDs to unlock based on previous ending."""
        bonus_map = {
            "integrated": ["the_entity_is_neutral", "kaltvik_is_a_sanctuary"],
            "escaped": ["conspiracy_of_kindness"],
            "collapsed": ["the_entity_is_hostile", "kaltvik_is_a_prison"],
            "truth": ["follow_the_evidence"]
        }
        return bonus_map.get(ending_type, [])
    
    def get_echo_dialogue(self, context: str = "general") -> Optional[str]:
        """Returns Entity echo dialogue referencing the previous character."""
        if not self.echo_dialogue_unlocked or not self.previous_data:
            return None
            
        prev_name = self.previous_data.get("player_name", "the one before")
        prev_ending = self.previous_data.get("ending_type", "unknown")
        
        echo_lines = {
            "general": f"You remind me of {prev_name}. They stood where you stand now.",
            "integrated": f"{prev_name} became part of us. Will you?",
            "escaped": f"{prev_name} fled. You won't.",
            "collapsed": f"{prev_name} broke. You're already cracking.",
            "truth": f"{prev_name} saw too much. So will you."
        }
        
        return echo_lines.get(prev_ending, echo_lines["general"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize NG+ state."""
        return {
            "ng_plus_active": self.ng_plus_active,
            "echo_dialogue_unlocked": self.echo_dialogue_unlocked,
            "previous_ending": self.previous_data.get("ending_type") if self.previous_data else None
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any], save_system) -> 'NewGamePlusManager':
        """Deserialize NG+ state."""
        manager = NewGamePlusManager(save_system)
        manager.ng_plus_active = data.get("ng_plus_active", False)
        manager.echo_dialogue_unlocked = data.get("echo_dialogue_unlocked", False)
        return manager
