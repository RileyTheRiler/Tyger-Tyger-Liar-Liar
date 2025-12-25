from typing import List, Dict, Any, Optional
from text_composer import TextComposer

class DiscoverySystem:
    def __init__(self, game_state, text_composer: TextComposer):
        self.state = game_state
        self.composer = text_composer
        self.discovered_clue_ids = set()

    def evaluate_passive_clues(self, scene_data: dict) -> List[dict]:
        """
        Check for passive clues in the scene.
        Returns a list of newly discovered clues.
        """
        new_clues = []
        passive_clues = scene_data.get("passive_clues", [])
        
        for p_clue in passive_clues:
            clue_id = p_clue.get("clue_id")
            condition = p_clue.get("visible_when", {})
            
            if clue_id and clue_id not in self.discovered_clue_ids:
                if self.composer._check_insert_condition(condition, self.state):
                    # Discovered!
                    self.discovered_clue_ids.add(clue_id)
                    # Add to game state board history
                    self.state.add_board_node({
                        "id": clue_id,
                        "type": "clue",
                        "status": "discovered"
                    })
                    new_clues.append({
                        "id": clue_id,
                        "style": p_clue.get("reveal_style", "panel")
                    })
        
        return new_clues

    def get_clue_list(self) -> List[dict]:
        """Return all discovered clues for the menu."""
        # In a real app, this would fetch from a database or pre-loaded clue dicts
        return [{"id": cid} for cid in self.discovered_clue_ids]
