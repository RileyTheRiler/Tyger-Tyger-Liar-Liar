
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mechanics import SkillSystem
from board import Board
from time_system import TimeSystem
from scene_manager import SceneManager # SceneManager is in src/scene_manager.py, not game.py

def test_board_integration():
    print("Initializing Game Systems...")
    
    # Setup
    # manager = SceneManager("scenes.json") # file existence doesn't matter much if we don't run loop
    time_sys = TimeSystem()
    skill_sys = SkillSystem()
    board = Board()
    player_state = {"sanity": 100, "reality": 100}
    
    manager = SceneManager(time_sys, board, skill_sys, player_state)
    manager.load_scenes_from_directory(".", "scenes.json")

    # 1. Check Initial Board State
    print("\n[Test 1] Initial Board State")
    t = manager.board.get_theory("i_want_to_believe")
    if t.status != "available":
        print(f"FAILED: Expected available, got {t.status}")
    else:
        print("PASSED: Theory is available.")

    # 2. Internalize
    print("\n[Test 2] Internalize 'I Want To Believe'")
    res = manager.board.start_internalizing("i_want_to_believe")
    print(f"Result: {res}")
    
    if manager.board.get_theory("i_want_to_believe").status != "internalizing":
        print("FAILED: Theory not internalizing.")
    else:
        print("PASSED: Theory internalizing.")

    # 3. Check Modifiers (Should be none yet)
    print("\n[Test 3] Check Modifiers (Pre-Active)")
    manager.update_board_effects()
    skill = manager.skill_system.get_skill("Paranormal Sensitivity")
    if skill.effective_level != skill.base_level:
         print(f"FAILED: Modifiers applied too early. Level: {skill.effective_level}")
    else:
         print("PASSED: No modifiers yet.")

    # 4. Advance Time (Partial)
    print("\n[Test 4] Advance Time 3h")
    manager.time_system.advance_time(3)
    # Theory needs 6h. Should still be internalizing.
    if manager.board.get_theory("i_want_to_believe").status != "internalizing":
        print("FAILED: Theory finished too early?")
    else:
        print("PASSED: Still internalizing.")

    # 5. Advance Time (Complete)
    print("\n[Test 5] Advance Time 4h (Total 7h)")
    manager.time_system.advance_time(4)
    # Should trigger completion
    if manager.board.get_theory("i_want_to_believe").status != "active":
        print(f"FAILED: Theory not active. Status: {manager.board.get_theory('i_want_to_believe').status}")
    else:
        print("PASSED: Theory Active!")

    # 6. Check Modifiers (Active)
    print("\n[Test 6] Check Modifiers (Active)")
    manager.update_board_effects()
    # "Paranormal Sensitivity": +2
    skill = manager.skill_system.get_skill("Paranormal Sensitivity")
    expected = skill.base_level + 2
    if skill.effective_level != expected:
        print(f"FAILED: Modifier not applied. Got {skill.effective_level}, expected {expected}")
        print(skill.modifiers)
    else:
        print(f"PASSED: Modifier applied correctly (+2). Current Level: {skill.effective_level}")

    # 7. Conflict Check
    print("\n[Test 7] Conflict Check")
    # Try to internalize "there_is_a_rational_explanation" which conflicts
    can, reason = manager.board.can_internalize("there_is_a_rational_explanation")
    if can:
        print(f"FAILED: Should be blocked. Result: {can}")
    else:
        print(f"PASSED: Blocked correctly. Reason: {reason}")
        
    print("\nALL TESTS COMPLETED.")

if __name__ == "__main__":
    test_board_integration()
