from player.game_state import GameState
from engine.board_system import internalize_theory, advance_theory_timers, show_board
from engine.input_handler import parse_command

def test_board_system():
    print("Running Board System Tests...")
    state = GameState()
    
    # 1. Test Internalize
    msg = internalize_theory("trust_no_one", state)
    assert "Started internalizing" in msg
    assert len(state.board["active"]) == 1
    assert state.board["active"][0]["id"] == "trust_no_one"
    print("  ✓ Internalize theory OK")

    # 2. Test Slot Limit
    internalize_theory("analytical_mind", state)
    assert len(state.board["active"]) == 2
    msg_fail = internalize_theory("some_other_theory", state)
    assert "No available slots" in msg_fail
    print("  ✓ Slot limit enforcement OK")

    # 3. Test Time Advancement and Completion
    # Initial perception: 2
    initial_perception = state.skills["Perception"]
    # trust_no_one gives +1 Perception, takes 6 hours.
    # analytical_mind gives -1 Perception, takes 4 hours.
    
    # Advance 4 hours
    advance_theory_timers(state, 4)
    assert "analytical_mind" in state.board["completed"]
    assert len(state.board["active"]) == 1 # trust_no_one still active
    assert state.board["active"][0]["remaining_time"] == 2
    assert state.skills["Perception"] == initial_perception - 1
    print("  ✓ Partial time advancement and completion OK")

    # Advance 2 more hours
    advance_theory_timers(state, 2)
    assert "trust_no_one" in state.board["completed"]
    assert len(state.board["active"]) == 0
    # Perception was 1, trust_no_one gives +1, should be 2 again (back to initial)
    assert state.skills["Perception"] == initial_perception
    # Wits was 1, trust_no_one gives +1, should be 2
    assert state.skills["Wits"] == 2
    print("  ✓ Full time advancement and skill modifiers OK")

    # 4. Test Parser
    cmd_theories = parse_command("theories", {})
    assert cmd_theories[0] == "theories"
    
    cmd_internalize = parse_command("internalize test_id", {})
    assert cmd_internalize[0] == "internalize"
    assert cmd_internalize[1] == "test_id"
    
    cmd_advance = parse_command("advance 10", {})
    assert cmd_advance[0] == "advance"
    assert cmd_advance[1] == 10
    print("  ✓ Input parser commands OK")

    print("\nALL BOARD TESTS PASSED!")

if __name__ == "__main__":
    test_board_system()
