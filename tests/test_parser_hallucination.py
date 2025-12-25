
import pytest
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.parser_hallucination import ParserHallucinationEngine
from engine.psychological_system import PsychologicalState

class MockPsychState:
    def __init__(self, sanity):
        self.player_state = {"sanity": sanity}

def test_hallucination_levels():
    # Sanity 100 -> Level 0
    engine = ParserHallucinationEngine(MockPsychState(100))
    assert engine.get_hallucination_level() == 0

    # Sanity 6 -> Level 1
    engine = ParserHallucinationEngine(MockPsychState(6))
    assert engine.get_hallucination_level() == 1

    # Sanity 3 -> Level 2
    engine = ParserHallucinationEngine(MockPsychState(3))
    assert engine.get_hallucination_level() == 2

    # Sanity 2 -> Level 3
    engine = ParserHallucinationEngine(MockPsychState(2))
    assert engine.get_hallucination_level() == 3

def test_trigger_queue():
    # Use Level 2 to ensure we hit the random generic response if no specific target
    engine = ParserHallucinationEngine(MockPsychState(3))

    # We need to mock random to ensure it triggers
    # Or just use a specific target that guarantees a hit
    engine.queue_trigger("parser_trigger", {"target": "mirror"})

    # Might not pop immediately due to delay
    msgs = []
    for _ in range(5):
        msgs.extend(engine.process_queue())

    assert len(msgs) > 0
    assert msgs[0] == "Reflections lie."

def test_verb_suggestions():
    engine = ParserHallucinationEngine(MockPsychState(3)) # Level 2
    verbs = engine.suggest_verbs()
    assert len(verbs) > 0
    assert verbs[0] in engine.hallucinated_verbs

def test_interception():
    engine = ParserHallucinationEngine(MockPsychState(1)) # Level 3 (Critical)

    # High chance of interception at level 3
    # We'll try multiple times to ensure we hit it
    intercepted = False
    for _ in range(20):
        inter, resp = engine.check_interception("ASK", "Sara")
        if inter:
            intercepted = True
            assert resp is not None
            break

    assert intercepted

def test_ghost_completions():
    engine = ParserHallucinationEngine(MockPsychState(3)) # Level 2

    # Test matching
    matches = engine.get_ghost_completions("call")
    assert "call Him" in matches

    # Test no match
    matches = engine.get_ghost_completions("xyz")
    assert len(matches) == 0

    # Test low sanity requirement
    engine = ParserHallucinationEngine(MockPsychState(100))
    matches = engine.get_ghost_completions("call")
    assert len(matches) == 0
