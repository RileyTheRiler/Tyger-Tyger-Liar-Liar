
import unittest
from typing import Dict, Any

# Mocking necessary classes for testing standalone
# In a real scenario, we'd import them, but imports might be tricky with the current structure 
# if not running from root. Assuming we can import from src.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from inventory_system import InventoryManager, Item, Evidence
from input_system import CommandParser

class TestWeek10Inventory(unittest.TestCase):
    def setUp(self):
        self.inv_manager = InventoryManager()
        self.parser = CommandParser()

    def test_item_creation_and_attributes(self):
        item = Item(
            id="flashlight",
            name="Flashlight",
            type="tool",
            description="A heavy mag-lite.",
            effects={"skill_modifiers": {"Perception": 1}},
            tags=["light_source"]
        )
        self.assertEqual(item.name, "Flashlight")
        self.assertIn("light_source", item.tags)
        self.assertEqual(item.get_skill_modifier("Perception"), 1)
        self.assertFalse(item.equipped)

    def test_equip_unequip_logic(self):
        item = Item(
            id="flashlight",
            name="Flashlight",
            type="tool",
            description="A heavy mag-lite.",
            effects={"skill_modifiers": {"Perception": 1}}
        )
        self.inv_manager.add_item(item)
        
        # Initially not equipped
        self.assertEqual(self.inv_manager.get_modifiers_for_skill("Perception"), 0)
        
        # Equip
        success = self.inv_manager.equip_item("flashlight")
        self.assertTrue(success)
        self.assertTrue(item.equipped)
        self.assertEqual(self.inv_manager.get_modifiers_for_skill("Perception"), 1)
        
        # Unequip
        success = self.inv_manager.unequip_item("Flashlight") # Case insensitive check
        self.assertTrue(success)
        self.assertFalse(item.equipped)
        self.assertEqual(self.inv_manager.get_modifiers_for_skill("Perception"), 0)

    def test_evidence_collection(self):
        ev = Evidence(
            id="ev_blood_01",
            description="A vial of blood.",
            type="physical",
            case_id="case_19"
        )
        self.inv_manager.add_evidence(ev)
        
        stored = self.inv_manager.evidence_collection.get("ev_blood_01")
        self.assertIsNotNone(stored)
        self.assertEqual(stored.case_id, "case_19")
        
        # Test Board string (simplified check)
        board_str = self.inv_manager.board.get_display_string()
        self.assertIn("ev_blood_01", board_str)

    def test_parser_verbs(self):
        # Check if new verbs are recognized
        actions = [
            ("search desk", "SEARCH"),
            ("scan room", "SEARCH"),
            ("photograph body", "PHOTOGRAPH"),
            ("bag clues", "TAKE"),
            ("collect knife", "TAKE"),
            ("equip gun", "EQUIP"),
            ("draw weapon", "EQUIP"),
            ("analyze fibers", "ANALYZE"),
            ("combine a with b", "COMBINE")
        ]
        
        for input_str, expected_verb in actions:
            normalized = self.parser.normalize(input_str)
            # normalize returns list of (verb, target)
            self.assertTrue(len(normalized) > 0, f"Failed to parse '{input_str}'")
            self.assertEqual(normalized[0][0], expected_verb, f"Expected {expected_verb} for '{input_str}', got {normalized[0][0]}")

if __name__ == '__main__':
    unittest.main()
