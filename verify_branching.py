import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('src/engine'))

from scene_manager import SceneManager
from branch_controller import BranchController
from attention_system import AttentionSystem

class TestBranchingIntegration(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.time_system = MagicMock()
        self.board = MagicMock()
        self.skill_system = MagicMock()
        self.player_state = {"current_location": "test_loc", "event_flags": set(), "sanity": 100}
        self.flashback_manager = MagicMock()
        self.npc_system = MagicMock()
        self.attention_system = AttentionSystem() # Use real attention system
        self.inventory_system = MagicMock()
        
        self.scene_manager = SceneManager(
            self.time_system,
            self.board,
            self.skill_system,
            self.player_state,
            self.flashback_manager,
            self.npc_system,
            self.attention_system,
            self.inventory_system
        )
        
        # Define complex test scene
        self.complex_scene = {
            "id": "complex_test",
            "name": "Complex Test Scene",
            "conditions": {
                "AND": [
                    {"attention_above": 20},
                    {"OR": [
                        {"skill_gte": {"Logic": 5}},
                        {"has_item": ["decoder_ring"]}
                    ]}
                ]
            }
        }
        
        # Enable Debug Mode
        self.scene_manager.branch_controller.debug_mode = True

    def tearDown(self):
        print("\n--- Controller Logs ---")
        for log in self.scene_manager.branch_controller.get_evaluation_log():
            print(log)
        print("-----------------------")

        
    def test_condition_access(self):
        print("\n=== Testing Complex Branching Conditions ===")
        
        # 1. Initial State: 0 Attention, No Skill, No Item -> Should Fail
        self.attention_system.attention_level = 0
        self.skill_system.get_skill.return_value.get_total.return_value = 0
        self.inventory_system.has_item.return_value = False
        
        success = self.scene_manager._check_conditions(self.complex_scene)
        print(f"Test 1 (All Fail): Expected False, Got {success}")
        self.assertFalse(success)
        
        # 2. Add Attention (25): Should still fail (Needs Skill OR Item)
        # Reset to 0 first just in case
        self.attention_system.attention_level = 0
        self.attention_system.add_attention(25, "Test Increment")
        success = self.scene_manager._check_conditions(self.complex_scene)
        print(f"Test 2 (Attention Only): Expected False, Got {success}")
        self.assertFalse(success)
        
        # 3. Add Skill (Logic 6): Should Pass (Att > 20 AND Skill > 5)
        self.skill_system.get_skill.return_value.get_total.return_value = 6
        success = self.scene_manager._check_conditions(self.complex_scene)
        print(f"Test 3 (Attention + Skill): Expected True, Got {success}")
        self.assertTrue(success)
        
        # 4. Remove Skill, Add Item: Should Pass (Att > 20 AND Item)
        self.skill_system.get_skill.return_value.get_total.return_value = 2
        self.inventory_system.has_item.return_value = True
        success = self.scene_manager._check_conditions(self.complex_scene)
        print(f"Test 4 (Attention + Item): Expected True, Got {success}")
        self.assertTrue(success)
        
        print("Branching Integration Verified Successfully.")

if __name__ == '__main__':
    unittest.main()
