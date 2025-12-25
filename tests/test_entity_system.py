"""
Verify Entity and Attention System Logic.
"""

import sys
import os
import unittest

# Adjust path to find src
sys.path.append(os.path.abspath('src'))

from attention_system import AttentionSystem
from integration_system import IntegrationSystem
from npc_system import NPCSystem, NPC
from game import Game

class TestEntitySystem(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.game.debug_mode = True

        # Setup dummy NPC for testing
        self.npc_data = {
            "id": "npc_test_bob",
            "name": "Test Bob",
            "location_id": "test_loc",
            "initial_trust": 50
        }
        self.game.npc_system.npcs["npc_test_bob"] = NPC(self.npc_data)

    def test_attention_taboos(self):
        """Test that performing taboos increases attention."""
        initial = self.game.attention_system.attention_level
        # "read_redacted" is the key we added
        res = self.game.attention_system.perform_taboo("read_redacted")
        if not res['success']:
             print(f"Taboo failed: {res.get('message')}")
        self.assertTrue(res['success'])
        self.assertGreater(self.game.attention_system.attention_level, initial)
        self.assertEqual(res['attention_gained'], 15)

    def test_curfew_check(self):
        """Test curfew violation logic."""
        # Set scene to outdoors (fake scene data) BEFORE advancing time, as advance_time might trigger listeners
        self.game.scene_manager.current_scene_id = "town_square_street"
        self.game.scene_manager.current_scene_data = {"name": "Street"}

        # Advance time to 23:00 (11 PM) - Start is 08:00
        # 15 hours = 900 minutes
        self.game.time_system.advance_time(900)
        self.game.scene_manager.current_scene_data = {"name": "Street"}

        # Advance time by 60 mins
        initial_attention = self.game.attention_system.attention_level
        self.game.on_time_passed(60)

        # Attention decay happens (-2 per hour), but curfew (+10) should net positive
        # Expected: Initial - 2 + 10 = Initial + 8

        # Note: on_time_passed calls decay_attention which subtracts 2 * (60/60) = 2
        # And curfew adds 10
        # So net +8

        self.assertGreater(self.game.attention_system.attention_level, initial_attention)

    def test_integration_detection(self):
        """Test NPC integration signs and parser commands."""
        npc = self.game.npc_system.get_npc("npc_test_bob")
        npc.set_integration_stage(2) # Fully Integrated

        # Test detection logic
        signs = self.game.integration_system.detect_integration_signs(npc.integration_stage)
        self.assertIn("thermal_drift", signs) # Always present at stage 2

    def test_parser_commands(self):
        """Test scan and ask commands."""
        # Mocking print to capture output would be ideal, but for now we just run to ensure no crash

        # Set player location to match NPC
        self.game.scene_manager.current_scene_id = "test_loc"
        # Ensure scene data exists
        self.game.scene_manager.current_scene_data = {"name": "Test Location", "objects": {}}

        # Run SCAN
        self.game.handle_parser_command("SCAN", "possession signs")

        # Run ASK
        self.game.handle_parser_command("ASK", "Test Bob where we first met")

if __name__ == '__main__':
    unittest.main()
