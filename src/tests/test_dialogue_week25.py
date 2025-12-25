
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

from engine.mechanics import SkillSystem
from content.dialogue_manager import DialogueManager
from engine.board import Board

class MockBoard(Board):
    def __init__(self):
        super().__init__()
        self.theories = {}

    def is_theory_active(self, tid):
        return False

class TestDialogueSystem(unittest.TestCase):
    def setUp(self):
        self.skill_system = SkillSystem()
        self.board = MockBoard()
        self.player_state = {"sanity": 100, "reality": 100}

        # Raise Attribute cap for tests to ensure skill level 5 is possible
        # Attributes default to cap 6, but check logic.
        # Attribute value (default 1) caps effective level.
        # So we must raise attribute value.
        for attr in self.skill_system.attributes.values():
            attr.value = 5

        # Setup Dialogue Manager
        self.dm = DialogueManager(self.skill_system, self.board, self.player_state)

        # Ensure interrupt data is loaded into skill system
        if not os.path.exists("data/interrupt_lines.json"):
            # Create dummy if missing
            with open("data/interrupt_lines.json", "w") as f:
                 f.write('{"Logic": ["Logic line"]}')
        self.dm._load_interrupt_lines()

    def test_load_dialogue(self):
        # Create a test dialogue file
        test_data = {
            "nodes": [
                {
                    "id": "start",
                    "text": "Hello",
                    "choices": [{"text": "Hi", "next": "end"}]
                },
                {
                    "id": "end",
                    "text": "Goodbye",
                    "choices": []
                }
            ]
        }
        import json
        os.makedirs("data/dialogues", exist_ok=True)
        with open("data/dialogues/test_load.json", "w") as f:
            json.dump(test_data, f)

        success = self.dm.load_dialogue("test_load", "data/dialogues")
        self.assertTrue(success)
        self.assertEqual(self.dm.current_node_id, "start")

    def test_passive_check(self):
        # Setup a node with passive check
        node = {
            "id": "test_passive",
            "text": "Something is hidden.",
            "passives": ["Logic"]
        }
        self.dm.nodes = {"test_passive": node}
        self.skill_system.skills["Logic"].base_level = 5 # Ensure success

        # Ensure Logic has interrupt lines for fallback
        self.dm.interrupt_data["Logic"] = ["Logic line"]

        self.dm.start_node("test_passive")

        render = self.dm.get_render_data()
        # Should have interjection: "[LOGIC] Logic line"
        # Note: Skill name in interjection is usually UPPERCASE in explicit passives code
        print(f"DEBUG INTERJECTIONS: {render['interjections']}")
        self.assertTrue(any("[LOGIC]" in i for i in render["interjections"]) or any("[Logic]" in i for i in render["interjections"]))

    def test_automatic_check_success(self):
        # Node with automatic check
        node = {
            "id": "check_node",
            "text": "Checking...",
            "check": {
                "skill": "Authority",
                "dc": 5,
                "success_next": "success",
                "fail_next": "fail"
            }
        }
        self.dm.nodes = {
            "check_node": node,
            "success": {"id": "success", "text": "Win"},
            "fail": {"id": "fail", "text": "Lose"}
        }

        self.skill_system.skills["Authority"].base_level = 5 # Ensure success

        self.dm.start_node("check_node")
        self.assertEqual(self.dm.current_node_id, "success")

    def test_automatic_check_fail(self):
        # Node with automatic check
        node = {
            "id": "check_node",
            "text": "Checking...",
            "check": {
                "skill": "Authority",
                "dc": 20, # Impossible
                "success_next": "success",
                "fail_next": "fail"
            }
        }
        self.dm.nodes = {
            "check_node": node,
            "success": {"id": "success", "text": "Win"},
            "fail": {"id": "fail", "text": "Lose"}
        }

        self.dm.start_node("check_node")
        self.assertEqual(self.dm.current_node_id, "fail")

if __name__ == '__main__':
    unittest.main()
