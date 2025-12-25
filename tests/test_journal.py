import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from journal_system import JournalManager

class TestJournalSystem(unittest.TestCase):
    def setUp(self):
        self.journal = JournalManager()

    def test_add_suspect(self):
        suspect_data = {
            "id": "nina_morrison",
            "name": "Nina Morrison",
            "age": 31,
            "role": "Sister",
            "notes": "Suspicious."
        }
        self.journal.add_suspect(suspect_data)
        self.assertIn("nina_morrison", self.journal.suspects)
        self.assertEqual(self.journal.suspects["nina_morrison"].status, "Active")

    def test_update_suspect_status(self):
        self.test_add_suspect()
        self.journal.update_suspect_status("nina_morrison", "Cleared")
        self.assertEqual(self.journal.suspects["nina_morrison"].status, "Cleared")

    def test_add_timeline_event(self):
        event_data = {
            "datetime_str": "2025-10-01T02:15",
            "title": "Disappearance",
            "details": "Jason vanished.",
            "tags": ["missing", "woods"]
        }
        self.journal.add_timeline_event(event_data)
        self.assertEqual(len(self.journal.timeline), 1)
        self.assertEqual(self.journal.timeline[0].title, "Disappearance")

    def test_filter_timeline(self):
        self.test_add_timeline_event()
        # Add another event
        self.journal.add_timeline_event({
            "datetime_str": "2025-10-02T10:00",
            "title": "Search Party",
            "details": "Nothing found.",
            "tags": ["police"]
        })
        
        missing_events = self.journal.get_timeline(tag_filter="missing")
        self.assertEqual(len(missing_events), 1)
        self.assertEqual(missing_events[0].title, "Disappearance")

    def test_open_question(self):
        q_data = {
            "id": "q1",
            "question": "Where is he?",
            "source": "Nina"
        }
        self.journal.add_question(q_data)
        self.assertIn("q1", self.journal.questions)
        self.assertEqual(self.journal.questions["q1"].status, "Open")
        
        self.journal.resolve_question("q1")
        self.assertEqual(self.journal.questions["q1"].status, "Resolved")

    def test_link_evidence(self):
        self.test_add_suspect()
        self.journal.link_evidence_to_suspect("nina_morrison", "red_scarf")
        self.assertIn("red_scarf", self.journal.suspects["nina_morrison"].evidence_links)

    def test_export_import(self):
        self.test_add_suspect()
        self.test_add_timeline_event()
        
        data = self.journal.export_state()
        
        new_journal = JournalManager()
        new_journal.load_state(data)
        
        self.assertIn("nina_morrison", new_journal.suspects)
        self.assertEqual(len(new_journal.timeline), 1)

if __name__ == '__main__':
    unittest.main()
