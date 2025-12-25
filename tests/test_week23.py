
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine.psychological_system import PsychologicalState
from engine.dream_system import DreamSystem
from engine.time_system import TimeSystem
from engine.mechanics import SkillSystem

class MockSkillSystem:
    def __init__(self):
        self.skills = {}

    def get_skill_total(self, name):
        return self.skills.get(name, 0)

    def set_skill(self, name, val):
        self.skills[name] = val

def test_dream_system_logic():
    player_state = {"sanity": 100}
    skill_sys = MockSkillSystem()
    dream_sys = DreamSystem(skill_sys, player_state)

    # Test 1: High Reason = Suppressed
    skill_sys.set_skill("Logic", 8)
    skill_sys.set_skill("Subconscious", 1)
    dream = dream_sys.generate_dream()
    assert dream["type"] == "suppressed"

    # Test 2: High Subconscious = Clarity
    skill_sys.set_skill("Logic", 2)
    skill_sys.set_skill("Subconscious", 7)
    dream = dream_sys.generate_dream()
    assert dream["clarity"] == 3
    assert "represents your guilt" in dream["description"]

    # Test 3: Prophetic
    skill_sys.set_skill("Subconscious", 3)
    skill_sys.set_skill("Intuition", 7)
    dream = dream_sys.generate_dream()
    assert dream["type"] == "prophetic"

    # Test 4: Nightmare (Low Sanity)
    player_state["sanity"] = 20
    dream = dream_sys.generate_dream()
    assert dream["type"] == "nightmare"

def test_sleep_integration():
    player_state = {"sanity": 50, "mental_load": 80}
    psych_state = PsychologicalState(player_state)
    skill_sys = MockSkillSystem()
    psych_state.set_skill_system(skill_sys)

    # Sleep Safe
    result = psych_state.attempt_sleep(location_safe=True)
    assert result["success"]
    assert player_state["sanity"] > 50 # Gained 20
    assert player_state["mental_load"] < 80 # Reduced
    assert result["dream"] is not None

    # Sleep Unsafe (Chance of failure, lets force fail if we can or just check possibility)
    # Since it uses random, we check that it runs without crash
    result = psych_state.attempt_sleep(location_safe=False)
    # Might fail or succeed depending on RNG

def test_time_system_events():
    ts = TimeSystem()
    ts.current_time = datetime(1995, 10, 14, 5, 0) # 5 AM

    events_triggered = []
    def callback():
        events_triggered.append(True)

    ts.schedule_event(60, callback, "Dawn") # Should fire at 6 AM

    ts.advance_time(30) # 5:30
    assert not events_triggered

    ts.advance_time(30) # 6:00
    assert events_triggered

def test_day_cycle_mechanic():
    # Implicit test via game loop logic, but we can verify data structure
    ts = TimeSystem()
    assert 6 in ts.day_cycle_events
    assert "Dawn" in ts.day_cycle_events[6]
