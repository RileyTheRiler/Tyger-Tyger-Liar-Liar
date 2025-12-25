
import unittest
import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "engine"))

from engine.scene_manager import SceneManager
from engine.text_composer import TextComposer, Archetype

class MockSystem:
    def __init__(self):
        self.skills = {}
        self.in_flashback = False
    def get_skill(self, name):
        class Skill:
            def __init__(self, val): self.effective_level = val
        return Skill(self.skills.get(name, 0))
    def roll_check(self, skill, dc):
        return {"success": True}
    def enter_flashback(self, pov): pass
    def exit_flashback(self): pass

class MockBoard:
    def __init__(self):
        self.theories = {}
    def get_theory(self, tid):
        return None

class MockTime:
    def __init__(self):
        from datetime import datetime
        self.current_time = datetime(1999, 10, 15, 12, 0)
        self.weather = "clear"

class TestSceneModular(unittest.TestCase):
    def setUp(self):
        self.player_state = {
            "sanity": 80,
            "reality": 90,
            "event_flags": set(),
            "skills": {"Paranormal Sensitivity": 6, "Logic": 2}
        }
        self.skill_system = MockSystem()
        self.skill_system.skills = self.player_state["skills"]
        self.board = MockBoard()
        self.time = MockTime()
        self.manager = SceneManager(self.time, self.board, self.skill_system, self.player_state, MockSystem()) # Flashback manager mocked
        self.composer = TextComposer(self.skill_system, self.board, self.player_state)

    def test_dynamic_inserts(self):
        scene_data = {
            "id": "test_scene",
            "text": "Base text.",
            "dynamic_inserts": [
                {
                    "trigger": "Paranormal Sensitivity > 5",
                    "text": "You feel a ghostly presence.",
                    "insert_at": "AFTER_BASE"
                },
                {
                    "trigger": "Logic > 5",
                    "text": "It makes perfect sense.",
                    "insert_at": "AFTER_BASE"
                }
            ]
        }

        # Manually load into manager cache
        self.manager.scenes["test_scene"] = scene_data
        loaded = self.manager.load_scene("test_scene")

        # Verify normalization
        self.assertTrue("inserts" in loaded["text"])
        inserts = loaded["text"]["inserts"]
        self.assertEqual(len(inserts), 2)

        # Test Composition
        composed = self.composer.compose(loaded["text"], Archetype.NEUTRAL, self.player_state)
        # print(f"\nComposed Text: {composed.full_text}")

        self.assertIn("Base text.", composed.full_text)
        self.assertIn("You feel a ghostly presence.", composed.full_text)
        self.assertNotIn("It makes perfect sense.", composed.full_text)

    def test_dynamic_inserts_no_duplication(self):
        """Ensure repeated loads don't duplicate dynamic inserts."""
        scene_data = {
            "id": "test_dupe",
            "text": {"base": "Base text.", "inserts": []},
            "dynamic_inserts": [
                {
                    "trigger": "Paranormal Sensitivity > 5",
                    "text": "Insert text."
                }
            ]
        }
        self.manager.scenes["test_dupe"] = scene_data

        # Load 1
        loaded1 = self.manager.load_scene("test_dupe")
        self.assertEqual(len(loaded1["text"]["inserts"]), 1)

        # Load 2 (Should not be 2)
        loaded2 = self.manager.load_scene("test_dupe")
        self.assertEqual(len(loaded2["text"]["inserts"]), 1)

    def test_parser_trigger(self):
        scene_data = {
            "id": "test_parser",
            "text": "Room.",
            "parser_triggers": [
                {
                    "command": "look sky",
                    "response": "The aurora bleeds.",
                    "effects": {"sanity": -5}
                }
            ]
        }
        self.manager.scenes["test_parser"] = scene_data
        self.manager.load_scene("test_parser")

        trigger = self.manager.check_parser_triggers("LOOK", "SKY")
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger["response"], "The aurora bleeds.")

        trigger_fail = self.manager.check_parser_triggers("LOOK", "FLOOR")
        self.assertIsNone(trigger_fail)

    def test_exit_conditions(self):
        scene_data = {
            "id": "test_exit",
            "text": "Room.",
            "exit_conditions": [
                {
                    "target": "forbidden_room",
                    "condition": "requires_flag('has_key')",
                    "locked_message": "The door is locked."
                }
            ]
        }
        self.manager.scenes["test_exit"] = scene_data
        self.manager.load_scene("test_exit")

        # Should be blocked
        msg = self.manager.check_exit_conditions("forbidden_room")
        self.assertEqual(msg, "The door is locked.")

        # Add flag
        self.player_state["event_flags"].add("has_key")

        # Should pass
        msg = self.manager.check_exit_conditions("forbidden_room")
        self.assertIsNone(msg)

if __name__ == '__main__':
    unittest.main()
