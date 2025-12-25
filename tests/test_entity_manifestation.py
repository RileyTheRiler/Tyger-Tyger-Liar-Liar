
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure src and project root are in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from game import Game
from engine.attention_system import AttentionSystem
from engine.endgame_manager import EndgameManager

class TestEntityManifestation(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.scene_manager = MagicMock()
        self.game.endgame_manager = MagicMock()
        # Suppress print output
        self.game.print = MagicMock() 

    def test_manifestation_trigger(self):
        """Verify attention > 100 triggers the manifestation scene."""
        # 1. Force Attention to > 100 (Buffer for decay)
        # Decay is 2 pts/hr. Testing 60 mins.
        self.game.attention_system.attention_level = 110
        
        # 2. Advance time to trigger check
        self.game.on_time_passed(60)
        
        # 3. Verify Scene Load
        self.game.scene_manager.load_scene.assert_called_with("entity_manifestation")
        
    def test_teleport_effect(self):
        """Verify teleport effect moves player and loads scene."""
        effect = {
            "teleport": {
                "target": "clinic_bed"
            }
        }
        
        self.game.apply_effects(effect)
        
        # Check location update
        self.assertEqual(self.game.player_state["current_location"], "clinic_bed")
        # Check scene load
        self.game.scene_manager.load_scene.assert_called_with("clinic_bed")

    def test_ending_effect(self):
        """Verify ending effect triggers endgame manager."""
        effect = {
            "ending": {
                "target": "integrated_forced"
            }
        }
        
        self.game.apply_effects(effect)
        
        # Check endgame trigger
        self.game.endgame_manager.trigger_ending.assert_called_with("integrated_forced")

if __name__ == "__main__":
    unittest.main()
