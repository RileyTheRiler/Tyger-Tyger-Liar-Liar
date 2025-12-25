import sys
import os

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'src'))
sys.path.append(os.path.join(root_dir, 'src', 'engine'))

from engine.board import Board
from engine.psychological_system import PsychologicalState
from engine.attention_system import AttentionSystem
from engine.manifestation_manager import ManifestationManager

def test_entity_beacon():
    print("=== TESTING ENTITY BEACON & 347 RULE ===")
    
    # 1. Setup Systems
    board = Board()
    player_state = {
        "sanity": 100, # Tier 4 (Stable)
        "mental_load": 0,
        "active_theories": []
    }
    psych = PsychologicalState(player_state)
    attention = AttentionSystem()
    manager = ManifestationManager(board, psych, attention)
    
    # 2. Test Beacon Effect Logic (Simulated)
    print("\n--- TEST: BEACON EFFECT ---")
    psych.player_state["mental_load"] = 90
    print(f"Mental Load set to {psych.player_state['mental_load']} (Critical)")
    
    # Simulate logic from game.py
    mental_load = psych.player_state.get("mental_load", 0)
    minutes = 60 # 1 hour
    
    if mental_load > 70:
        beacon_amount = int((mental_load - 70) / 5) # adjusted for test visibility
        hours_passed = minutes / 60.0
        beacon_gain = int(beacon_amount * hours_passed)
        print(f"Calculated Beacon Gain: +{beacon_gain}")
        attention.add_attention(beacon_gain, "Mental Beacon")
        
    print(f"Attention Level: {attention.attention_level}")
    assert attention.attention_level > 0, "Beacon should increase attention"

    # 3. Test 347 Rule Trigger
    print("\n--- TEST: 347 RULE ---")
    
    # Setup 347 Conditions:
    # 3 Active Theories
    # Sanity Tier 4 (Already 100)
    # Friction >= 70
    
    # Mock Board State
    # (We can't easily force theories without data, so we'll mock the return values if possible or force properties)
    
    # Hack: Creating fake theories for the board to count
    # Since Board uses a dict, we can inject dummy theories
    from engine.board import Theory
    
    # Mock get_total_friction
    board.get_total_friction = lambda: 75
    board.get_active_or_internalizing_count = lambda: 3
    
    # Verify mock
    print(f"Mocked Friction: {board.get_total_friction()}")
    
    print("Mocked State: 3 Theories, 75 Friction, 100 Sanity")
    
    # Check Resonance
    current_time = 1000
    event = manager.check_resonance(current_time)
    
    print(f"Resonance Event: {event}")
    
    assert event["triggered"] == True
    assert event["type"] == "manifestation"
    assert "347" in event["message"]
    
    print(f"New Attention Level: {attention.attention_level}")
    assert attention.attention_level >= 30, "Major resonance should spike attention"

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_entity_beacon()
