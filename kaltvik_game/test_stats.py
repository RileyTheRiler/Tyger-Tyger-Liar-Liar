from player.game_state import GameState
from engine.character_sheet import categorize_skills
from engine.skill_check import roll_skill_check
from engine.input_handler import parse_command

def test_character_system():
    print("Running Character System Tests...")
    state = GameState()
    
    # 1. Test GameState
    assert state.attributes["reason"] == 3
    assert state.skills["Logic"] == 2
    print("  ✓ GameState initialization OK")

    # 2. Test Skill Categorization
    categories = categorize_skills(state.skills)
    assert "Reason" in categories
    assert any(s[0] == "Logic" for s in categories["Reason"])
    print("  ✓ Skill categorization OK")

    # 3. Test Skill Check
    # Force a success by using a high skill level and low DC
    # (Actually roll_skill_check is random, but we can test the logic)
    result, roll = roll_skill_check("Logic", 10, 2, state=state)
    assert result == "success"
    print(f"  ✓ Skill check success test OK (Roll: {roll})")

    # 4. Test White Check Locking
    # Second check with same white_id should be locked
    state.checked_whites = set()
    res1, roll1 = roll_skill_check("Logic", 2, 12, white_id="test_id", is_red=False, state=state)
    assert "test_id" in state.checked_whites
    
    res2, roll2 = roll_skill_check("Logic", 2, 12, white_id="test_id", is_red=False, state=state)
    assert res2 == "locked"
    print("  ✓ White check locking logic OK")

    # 5. Test Input Parser
    cmd_char = parse_command("character", {})
    assert cmd_char[0] == "character"
    
    cmd_roll = parse_command("roll Logic 10", {})
    assert cmd_roll[0] == "roll"
    assert cmd_roll[1] == ("Logic", 10)
    
    cmd_examine = parse_command("examine aurora", {"aurora": "test"})
    assert cmd_examine[0] == "examine"
    print("  ✓ Input parser commands OK")

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    test_character_system()
