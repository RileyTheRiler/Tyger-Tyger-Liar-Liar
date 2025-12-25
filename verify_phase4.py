import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from dice import DiceSystem, CheckResult

def verify_phase4():
    print("Verifying Phase 4: 2d6 Resolution + Manual Rolling...")
    
    gs = GameState()
    gs.attributes["REASON"] = 4
    gs.skills["Logic"] = 2
    
    dice = DiceSystem()
    
    # 1. Success check
    print("\n--- Test 1: Automatic Success ---")
    modifier = gs.get_effective_skill("Logic") # 6
    result = dice.resolve_check("Logic", modifier, dc=9, manual_roll=4) # 4+6=10 (Success)
    
    if result.result == CheckResult.SUCCESS:
        print("[SUCCESS] Success check verified.")
    else:
        print(f"[FAILURE] Success check failed. Result: {result.result}")

    # 2. Partial Success
    print("\n--- Test 2: Partial Success (Fail by 1) ---")
    # DC 11. Modifier 6. Roll 4. Total 10. Margin -1.
    result = dice.resolve_check("Logic", modifier, dc=11, manual_roll=4)
    
    if result.result == CheckResult.PARTIAL_SUCCESS:
        print("[SUCCESS] Partial success check verified.")
        print(f"Costs applied: {result.costs}")
    else:
        print(f"[FAILURE] Partial success check failed. Result: {result.result}")

    # 3. Manual Mode
    print("\n--- Test 3: Manual Mode ---")
    dice.set_manual_mode(True, callback=lambda: 12) # Force 12
    result = dice.resolve_check("Logic", modifier, dc=15)
    
    if result.result == CheckResult.CRITICAL_SUCCESS:
        print("[SUCCESS] Manual mode / Critical success verified.")
    else:
        print(f"[FAILURE] Manual mode check failed. Result: {result.result}")

    # 4. Stress Modifiers
    print("\n--- Test 4: Stress Modifiers ---")
    dice.set_stress_modifier(-2)
    # DC 9. Modifier 6. Stress -2. Roll 4. Total 8. Margin -1.
    result = dice.resolve_check("Logic", modifier, dc=9, manual_roll=4, allow_partial=False)
    
    if result.result == CheckResult.FAILURE:
        print("[SUCCESS] Stress modifier verified (Success turned to Failure).")
    else:
        print(f"[FAILURE] Stress modifier failed. Result: {result.result}")

if __name__ == "__main__":
    verify_phase4()
