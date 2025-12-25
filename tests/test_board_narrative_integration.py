
import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
src_path = os.path.join(project_root, 'src')
engine_path = os.path.join(src_path, 'engine')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

print(f"DEBUG: sys.path[0] = {sys.path[0]}")
print(f"DEBUG: src exists: {os.path.exists(src_path)}")
if os.path.exists(src_path):
    print(f"DEBUG: src contents: {os.listdir(src_path)}")

from engine.text_composer import TextComposer, Archetype
from engine.mechanics import SkillSystem
from engine.board import Board, Theory

class TestBoardNarrativeIntegration(unittest.TestCase):
    def setUp(self):
        # Mock Theory Data
        self.theory_id = "theory_intentional_crash"
        self.theory_data = {
            "name": "Intentional Crash",
            "category": "Reason",
            "description": "It wasn't an accident.",
            "status": "active",
            "linked_evidence": ["red_car"]
        }
        
        # Mock Skill System with Theory Commentary
        self.skill_system = SkillSystem()
        self.skill_system.theory_commentary = {
            self.theory_id: {
                "skill": "LOGIC",
                "text": "The physics of the turn... it wasn't an accident.",
                "color": "blue"
            }
        }
        
        # Mock Board
        self.board = Board()
        theory = Theory(self.theory_id, self.theory_data)
        theory.status = "active"
        theory.linked_evidence = ["red_car"]
        self.board.theories = {self.theory_id: theory}
        
        self.composer = TextComposer(skill_system=self.skill_system, board=self.board)
        self.composer.debug_mode = True
        
    def test_theory_voice_interjection(self):
        """Verify that a theory can interject in the narrative."""
        # Force the random roll to succeed by mocking random
        import random
        random.randint = MagicMock(return_value=6) # 2d6 = 12, always > 10
        
        player_state = {
            "active_theories": [self.theory_id],
            "sanity": 100.0,
            "skills": {}
        }
        
        text_data = {"base": "You look at the wreckage."}
        result = self.composer.compose(text_data, Archetype.NEUTRAL, player_state)
        
        self.assertIn("[LOGIC]: \"The physics of the turn... it wasn't an accident.\"", result.full_text)
        self.assertIn("voice:LOGIC", result.debug_info.get("layers", []))

    def test_evidence_echoes(self):
        """Verify that evidence keywords are highlighted in the text."""
        player_state = {
            "active_theories": [self.theory_id],
            "sanity": 100.0
        }
        
        # Text containing "red car" (keyword from "red_car" evidence)
        text_data = {"base": "The red car was lying in the ditch."}
        result = self.composer.compose(text_data, Archetype.NEUTRAL, player_state)
        
        # Check for italics highlight
        self.assertIn("*red car*", result.full_text.lower())
        self.assertIn("evidence_echoes", result.debug_info.get("layers", []))

    def test_ui_distortion_factor(self):
        """Verify board distortion factor calculation."""
        # Baseline
        self.assertEqual(self.board.get_ui_distortion_factor(100.0), 0.0)
        
        # Low Sanity (50) -> 0.5 factor
        self.assertEqual(self.board.get_ui_distortion_factor(50.0), 0.5)
        
        # Add a contradiction
        theory = self.board.get_theory(self.theory_id)
        theory.contradictions = 2 # +0.2 factor
        
        # Sanity 50 (0.5) + Contradictions (0.2) = 0.7
        self.assertAlmostEqual(self.board.get_ui_distortion_factor(50.0), 0.7)

if __name__ == "__main__":
    unittest.main()
