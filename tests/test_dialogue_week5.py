import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dialogue_manager import DialogueManager

class TestDialogueWeek5(unittest.TestCase):
    def setUp(self):
        self.mock_skill_system = MagicMock()
        self.mock_board = MagicMock()
        self.player_state = {
            "sanity": 100,
            "reality": 100,
            "failed_reds": [],
            "checked_whites": []
        }
        self.dm = DialogueManager(self.mock_skill_system, self.mock_board, self.player_state)
        
        # Create temp dialogue and interrupt files
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists("data/dialogues"): os.makedirs("data/dialogues")
        
        with open("data/interrupt_lines.json", "w") as f:
            f.write('{"Empathy": {"test_dialogue": "Interruption text."}}')
            
        with open("data/dialogues/test_dialogue.json", "w") as f:
            f.write('''
            {
              "scene_id": "test_dialogue",
              "lines": [
                {
                  "id": "start",
                  "speaker": "NPC",
                  "text": "Hello.",
                  "choices": [
                    { "id": "check_choice", "text": "Run Check", "next": "check_node" },
                    { "id": "theory_choice", "text": "Theory Choice", "next": "theory_node", "require_theory": "TheoryA" }
                  ],
                  "passives": ["Empathy"]
                },
                {
                  "id": "check_node",
                  "speaker": "System",
                  "text": "Checking...",
                  "check": {
                    "skill": "Logic",
                    "dc": 10,
                    "white_id": "logic_check",
                    "success_next": "success_node",
                    "fail_next": "fail_node"
                  }
                },
                { "id": "success_node", "speaker": "NPC", "text": "Success!" },
                { "id": "fail_node", "speaker": "NPC", "text": "Fail!" },
                { "id": "theory_node", "speaker": "NPC", "text": "Theory worked!" }
              ]
            }
            ''')
        
        # Reload dm because it loads interrupt data in __init__
        self.dm = DialogueManager(self.mock_skill_system, self.mock_board, self.player_state)

    def test_passive_interrupt(self):
        # Force skill check to succeed
        self.mock_skill_system.roll_check.return_value = {"success": True}
        
        self.dm.load_dialogue("test_dialogue", "data/dialogues")
        data = self.dm.get_render_data()
        
        self.assertIn("[Empathy] Interruption text.", data['interjections'])

    def test_theory_requirement_locked(self):
        self.mock_board.is_theory_active.return_value = False
        
        self.dm.load_dialogue("test_dialogue", "data/dialogues")
        data = self.dm.get_render_data()
        
        theory_choice = next(c for c in data['choices'] if c['text'] == "Theory Choice")
        self.assertFalse(theory_choice['enabled'])
        self.assertIn("TheoryA", theory_choice['reason'])

    def test_theory_requirement_unlocked(self):
        self.mock_board.is_theory_active.return_value = True
        
        self.dm.load_dialogue("test_dialogue", "data/dialogues")
        data = self.dm.get_render_data()
        
        theory_choice = next(c for c in data['choices'] if c['text'] == "Theory Choice")
        self.assertTrue(theory_choice['enabled'])

    def test_automatic_check_success(self):
        self.mock_skill_system.roll_check.return_value = {"success": True}
        
        self.dm.load_dialogue("test_dialogue", "data/dialogues")
        # Go to check_node
        self.dm.select_choice(0) 
        
        # Should have transitioned to success_node automatically
        self.assertEqual(self.dm.current_node_id, "success_node")
        self.assertIn("logic_check", self.player_state["checked_whites"])

    def test_automatic_check_fail(self):
        self.mock_skill_system.roll_check.return_value = {"success": False}
        
        self.dm.load_dialogue("test_dialogue", "data/dialogues")
        # Go to check_node
        self.dm.select_choice(0) 
        
        # Should have transitioned to fail_node automatically
        self.assertEqual(self.dm.current_node_id, "fail_node")

if __name__ == "__main__":
    unittest.main()
