import pytest
from psychological_system import PsychologicalSystem, SanityState

def test_sanity_initialization():
    player_state = {}
    sys = PsychologicalSystem(player_state)
    assert sys.get_sanity() == 100.0
    assert sys.get_sanity_state() == SanityState.CLEAR

def test_sanity_modification():
    player_state = {"sanity": 50.0}
    sys = PsychologicalSystem(player_state)
    sys.modify_sanity(-20)
    assert sys.get_sanity() == 30.0
    assert sys.get_sanity_state() == SanityState.PARANOID
    sys.modify_sanity(30)
    assert sys.get_sanity() == 60.0
    assert sys.get_sanity_state() == SanityState.DISTRACTED

def test_paranoia_vector():
    player_state = {}
    sys = PsychologicalSystem(player_state)
    assert sys.get_paranoia_level() == 0.0
    sys.update_paranoia("isolation", 10.0)
    assert sys.get_paranoia_level() == 10.0
    assert player_state["paranoia"]["magnitude"] == 10.0

def test_text_distortion():
    player_state = {"sanity": 10.0} # Fractured
    sys = PsychologicalSystem(player_state)
    text = "The truth is you see the door."
    distorted = sys.get_text_distortion(text)
    assert distorted != text
    # Check if some words are replaced (stochastic test, might flake if not careful, but probability is high)
    # With sanity 10, probability is (60-10)/100 = 0.5.

def test_clarity_index():
    player_state = {"sanity": 95}
    sys = PsychologicalSystem(player_state)
    assert sys.get_clarity_index() == "Lucid"
    sys.set_sanity(10)
    assert sys.get_clarity_index() == "Lost"
