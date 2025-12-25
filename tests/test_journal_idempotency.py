
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'engine'))

from game import Game

class TestJournalIdempotency(unittest.TestCase):
    def setUp(self):
        # Suppress output during tests
        self.game = Game()
        self.game.print = MagicMock()

    def test_idempotency(self):
        """Test that duplicate events do not create duplicate journal entries."""
        # First event
        self.game.log_event("evidence_found", name="Unique Item", description="Found once.")

        entries_count = len(self.game.journal.entries)
        self.assertEqual(entries_count, 1)

        # Duplicate event
        self.game.log_event("evidence_found", name="Unique Item", description="Found once.")

        # Count should remain same
        self.assertEqual(len(self.game.journal.entries), 1)

        # Different event
        self.game.log_event("evidence_found", name="Unique Item", description="Found twice (different desc).")
        self.assertEqual(len(self.game.journal.entries), 2)

if __name__ == '__main__':
    unittest.main()
