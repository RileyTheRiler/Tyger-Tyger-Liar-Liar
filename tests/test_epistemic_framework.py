import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tyger_game.engine.character import Character
from tyger_game.engine.alignment_system import AlignmentSystem
from tyger_game.engine.paradigm_system import ParadigmManager, PARADIGM_DB
from tyger_game.engine.board_system import BoardSystem, BoardNode
from tyger_game.engine.skill_checks import format_check_result, CheckResult
from tyger_game.utils.constants import ALIGNMENTS

class TestEpistemicFramework(unittest.TestCase):
    def setUp(self):
        self.char = Character("Investigator")
        # Ensure clean state
        self.char.alignment_scores = {"believer": 0, "skeptic": 0, "order": 0, "chaos": 0}

    def test_alignment_thresholds(self):
        print("\n--- Testing Alignment Thresholds ---")
        
        # 1. Test Increment
        self.char.alignment_scores["believer"] = 3
        
        # 2. Trigger Threshold (3 -> 4)
        vision_path = AlignmentSystem.modify_alignment(self.char, "believer", 1)
        self.assertEqual(self.char.alignment_scores["believer"], 4)
        self.assertIsNotNone(vision_path)
        print(f"Triggered Vision Quest: {vision_path}")

        # 3. Test No Trigger (4 -> 5)
        vision_path_2 = AlignmentSystem.modify_alignment(self.char, "believer", 1)
        self.assertEqual(self.char.alignment_scores["believer"], 5)
        self.assertIsNone(vision_path_2)

        # 4. Check Archetype Calculation
        # Believer (5) > Skeptic (0)
        # Order (0) vs Chaos (0) -> Default Order? Logic says >= so Order
        archetype = AlignmentSystem.calculate_archetype(self.char)
        self.assertEqual(archetype, ALIGNMENTS["FUNDAMENTALIST"]) # Believer + Order

        # Shift to Chaos
        self.char.alignment_scores["chaos"] = 5
        archetype = AlignmentSystem.calculate_archetype(self.char)
        self.assertEqual(archetype, ALIGNMENTS["TRUTH_SEEKER"]) # Believer + Chaos
        print(f"Archetype Shifted to: {archetype}")

    def test_paradigm_lifecycle(self):
        print("\n--- Testing Paradigm Lifecycle ---")
        pid = "simulation_hypothesis"
        
        # 1. Start Internalizing
        success = ParadigmManager.start_internalizing(self.char, pid)
        self.assertTrue(success)
        self.assertEqual(len(self.char.paradigms), 1)
        self.assertEqual(self.char.paradigms[0]["status"], "internalizing")
        
        # 2. Advance Time (Not enough)
        ParadigmManager.advance_time(self.char, 2)
        self.assertEqual(self.char.paradigms[0]["progress"], 2)
        self.assertFalse(self.char.paradigms[0]["completed"])

        # 3. Complete
        # Total time needed is 6. So 4 more.
        ParadigmManager.advance_time(self.char, 4)
        self.assertTrue(self.char.paradigms[0]["completed"])
        self.assertEqual(self.char.paradigms[0]["status"], "completed")
        print(f"Completed Paradigm: {pid}")

        # 4. Check Permanent Effects (Alignment Shift)
        # Simulation Hypothesis gives Skeptic+1, Chaos+2
        # Current scores (from clean setup for this test? No, setUp runs every time)
        # setUp resets char. So base is 0.
        # Skeptic: 1, Chaos: 2
        self.assertEqual(self.char.alignment_scores["skeptic"], 1)
        self.assertEqual(self.char.alignment_scores["chaos"], 2)

    def test_board_logic_skeptic_filter(self):
        print("\n--- Testing Deduction Board Epistemic Filter ---")
        board = BoardSystem()
        
        # Setup Nodes
        node_fact = BoardNode("bullet", "Bullet Casing", "FACT", "HARD")
        node_paranormal = BoardNode("ghost", "Ghost Photo", "ANOMALY", "SOFT")
        board.add_node(node_fact)
        board.add_node(node_paranormal)

        # Case 1: Neutral Alignment (0 vs 0) -> Should Allow
        allowed = board._validate_connection_alignment(node_fact, node_paranormal, self.char)
        self.assertTrue(allowed, "Neutral character should be flexible.")

        # Case 2: Hard Skeptic (Skeptic 10 vs Believer 0)
        self.char.alignment_scores["skeptic"] = 10
        self.char.active_alignment = "Debunker"
        
        allowed_skeptic = board._validate_connection_alignment(node_fact, node_paranormal, self.char)
        self.assertFalse(allowed_skeptic, "Skeptic should REJECT Soft Anomaly connection.")
        print("Skeptic correctly rejected soft paranormal connection.")

    def test_skill_voices(self):
        print("\n--- Testing Skill Voices ---")
        # Visual check
        details = {'success': True, 'total': 15, 'base_roll': 10, 'skill_level': 5, 'difficulty': 10, 'critical_success': False, 'critical_failure': False}
        res = CheckResult(True, 15, details, 'white')
        
        text = format_check_result(res, "Deduction")
        self.assertIn("The Cold Logic", text)
        print(f"Output: {text}")

if __name__ == '__main__':
    unittest.main()
