
import unittest
from engine.narrative_memory_system import NarrativeMemorySystem, NarrativeEvent

class MockTimeSystem:
    def __init__(self):
        self.current_time = 1000.0
        self.start_time = 0.0

class MockTimeSystemWrapper:
    def __init__(self):
        self.current_time = MockTimeSystem()
        self.current_time.current_time = 1000.0
        self.start_time = MockTimeSystem()
        self.start_time.current_time = 0.0

    @property
    def current_time_val(self):
        return self.current_time.current_time

class SimpleMockTime:
    def __init__(self):
        self._current = 1000.0
        self._start = 0.0

    @property
    def current_time(self):
        class T:
            pass
        t = T()
        t.timestamp = lambda: self._current
        t.__sub__ = lambda o: class_diff(self._current, o.timestamp() if hasattr(o, 'timestamp') else 0)
        return t

    @property
    def start_time(self):
         class T:
            pass
         t = T()
         t.timestamp = lambda: self._start
         return t

class ClassDiff:
    def __init__(self, val):
        self.val = val
    def total_seconds(self):
        return self.val * 60

class MockTimeSystemV2:
    def __init__(self):
        self.current_val = 1000
        self.start_val = 0

    @property
    def current_time(self):
        return self

    @property
    def start_time(self):
        return self

    def __sub__(self, other):
        return ClassDiff(self.current_val - self.start_val)

    def timestamp(self):
        return self.current_val

class TestNarrativeMemory(unittest.TestCase):
    def setUp(self):
        self.player_state = {
            "archetype": "neutral",
            "sanity": 100.0,
            "reality": 100.0
        }
        self.time_system = MockTimeSystemV2()
        self.memory_system = NarrativeMemorySystem(
            text_composer=None,
            player_state=self.player_state,
            time_system=self.time_system
        )

    def test_log_and_recall(self):
        event_id = "test_event"
        text = "This is a test event."
        self.memory_system.log_event(event_id, text, 1)

        recalled = self.memory_system.recall_event(event_id)
        self.assertIn("This is a test event.", recalled)

    def test_drift_effects(self):
        event_id = "drift_event"
        text = "I definitely saw a ghost clearly."
        self.memory_system.log_event(event_id, text, 1)

        # Advance time significantly
        self.time_system.current_val += 20000

        # Lower reality to trigger drift effects
        self.player_state["reality"] = 40.0

        recalled = self.memory_system.recall_event(event_id)

        # Expect changes
        self.assertNotEqual(text, recalled)
        self.assertTrue("maybe" in recalled or "..." in recalled or "hazy" in recalled)

    def test_explicit_false_memory(self):
        self.memory_system.inject_explicit_false_memory()
        recalled = self.memory_system.recall_event("arrival_memory")

        # Should contain the corrupted text
        self.assertIn("black sedan", recalled)
        self.assertIn("blood", recalled)

        # Should contain injected contradiction due to high drift
        self.assertTrue(any(x in recalled for x in ["Wait", "No", "found you"]))

if __name__ == '__main__':
    unittest.main()
