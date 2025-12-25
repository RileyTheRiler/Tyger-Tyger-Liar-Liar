
import pytest
import time
from engine.reality_checker import RealityConsistencyChecker, RealityFact

def test_reality_checker_basic():
    checker = RealityConsistencyChecker(debug_mode=True)

    # Register a fact
    checker.register_fact(
        subject="player",
        attribute="location",
        value="Bedroom",
        timestamp=100,
        location_id="bedroom",
        is_distorted=False,
        source_text="You are in your bedroom."
    )

    assert len(checker.facts) == 1
    assert checker.facts[0].value == "Bedroom"

def test_reality_checker_contradiction_strict():
    checker = RealityConsistencyChecker(debug_mode=True)

    # Fact 1: Player is in Bedroom at 10:00 (600 mins)
    checker.register_fact("player", "location", "Bedroom", 600, "bedroom", False, "You wake up.")

    # Fact 2: Player is in Kitchen at 10:00 (600 mins) - Contradiction! (Same time)
    checker.register_fact("player", "location", "Kitchen", 600, "kitchen", False, "You are making coffee.")

    assert len(checker.contradictions) == 1
    c = checker.contradictions[0]
    assert "Simultaneous conflicting facts" in c.message

def test_reality_checker_movement_valid():
    checker = RealityConsistencyChecker(debug_mode=True)

    # Fact 1: Bedroom at 600
    checker.register_fact("player", "location", "Bedroom", 600, "bedroom", False, "Start")

    # Fact 2: Kitchen at 601 (Time advanced by 1 min)
    # This should NOT be a contradiction with threshold=0 for location
    checker.register_fact("player", "location", "Kitchen", 601, "kitchen", False, "Moved")

    assert len(checker.contradictions) == 0

def test_reality_checker_distorted_ignore():
    checker = RealityConsistencyChecker(debug_mode=True)

    # Fact 1: Real
    checker.register_fact("player", "status", "Alive", 600, "bedroom", False, "You feel fine.")

    # Fact 2: Distorted (Hallucination) says Dead
    checker.register_fact("player", "status", "Dead", 600, "bedroom", True, "THE VOID CLAIMS YOU.")

    # Should NOT be a contradiction because one is distorted
    assert len(checker.contradictions) == 0

def test_reality_checker_ignored_subject():
    checker = RealityConsistencyChecker(debug_mode=True)

    # Fact 1: Weather is Sunny
    checker.register_fact("weather", "status", "Sunny", 600, "outdoors", False, "It is sunny.")

    # Fact 2: Weather is Rainy immediately after
    checker.register_fact("weather", "status", "Rainy", 600, "outdoors", False, "It is raining.")

    # Should be ignored because "weather" is in ignored_subjects
    assert len(checker.contradictions) == 0

def test_report_generation():
    checker = RealityConsistencyChecker()
    checker.register_fact("a", "b", "c", 1, "loc", False, "src")
    checker.register_fact("a", "b", "d", 1, "loc", False, "src2") # Contradiction (Threshold 2 for non-location)

    report = checker.generate_report()
    assert "Contradictions Found: 1" in report
    assert "Reality Consistency Report" in report
