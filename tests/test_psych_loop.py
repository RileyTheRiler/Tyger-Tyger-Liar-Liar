
import sys
import os
sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('src/engine'))

from engine.psychological_system import PsychologicalState
from engine.text_composer import TextComposer, Archetype

def test_psychological_state():
    print("Testing PsychologicalState...")
    player_state = {}
    psych = PsychologicalState(player_state)

    # Test Init
    assert psych.stress == 0
    assert psych.doubt == 0
    assert psych.obsession == 0
    assert psych.stability == 100.0

    # Test Modify
    psych.add_stress(60, "Test")
    assert psych.stress == 60
    assert "mental_load" in player_state # Legacy sync
    assert player_state["mental_load"] == 60

    psych.stability = 40
    assert psych.get_stability_tier() == 2 # 25-49

    print("PsychologicalState Tests Passed.")

def test_text_distortion():
    print("Testing TextComposer Distortions...")
    player_state = {"stress": 90, "doubt": 0}
    composer = TextComposer()

    text = "The quick brown fox jumps over the lazy dog."

    # Stress Distortion
    distorted = composer._apply_stress_distortion(text, 90)
    print(f"Original: {text}")
    print(f"Stressed: {distorted}")
    assert text != distorted

    # Doubt Distortion
    player_state["stress"] = 0
    player_state["doubt"] = 80
    doubt_text = "The killer was definitely in the room. He left a clear fingerprint."
    filtered = composer._apply_doubt_filter(doubt_text, 80)
    print(f"Original: {doubt_text}")
    print(f"Doubting: {filtered}")
    assert doubt_text != filtered

    print("TextComposer Tests Passed.")

if __name__ == "__main__":
    test_psychological_state()
    test_text_distortion()
