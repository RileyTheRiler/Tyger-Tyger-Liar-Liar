
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'engine'))

from game import Game
from journal_system import JournalManager
from inventory_system import Evidence

class TestJournalIntegration(unittest.TestCase):
    def setUp(self):
        # Suppress output during tests
        self.game = Game()
        self.game.print = MagicMock()

    def test_auto_journal_evidence(self):
        """Test that finding evidence creates a journal entry."""
        # Simulate finding evidence via log_event
        self.game.log_event("evidence_found", name="Test Evidence", description="A test item.")

        # Check journal
        entries = self.game.journal.entries
        self.assertTrue(len(entries) > 0, "Journal should have an entry")
        last_entry = entries[-1]
        self.assertIn("Evidence", last_entry.title)
        self.assertEqual(last_entry.what_happened, "A test item.")
        self.assertIn("evidence", last_entry.tags)

    def test_auto_journal_theory(self):
        """Test that proving a theory creates a journal entry."""
        self.game.log_event("theory_proven", theory_id="theory_alpha")

        entries = self.game.journal.entries
        last_entry = entries[-1]
        self.assertIn("Theory Proven", last_entry.title)
        self.assertIn("theory", last_entry.tags)
        self.assertEqual(last_entry.meaning, "My understanding of the case is shifting.")

    def test_confidence_logic(self):
        """Test that high skills increase confidence."""
        # Set high skills
        # Need to set attribute cap higher first, as default cap is 6
        self.game.skill_system.attributes["REASON"].cap = 10
        self.game.skill_system.attributes["REASON"].value = 10
        self.game.skill_system.skills["Logic"].base_level = 8

        # Use "Pattern Recognition" instead of "Intuition" based on skills.json
        self.game.skill_system.attributes["INTUITION"].cap = 10
        self.game.skill_system.attributes["INTUITION"].value = 10
        self.game.skill_system.skills["Pattern Recognition"].base_level = 8

        self.game.log_event("theory_proven", theory_id="theory_beta")

        entries = self.game.journal.entries
        last_entry = entries[-1]
        self.assertEqual(last_entry.confidence, "High")

if __name__ == '__main__':
    unittest.main()
