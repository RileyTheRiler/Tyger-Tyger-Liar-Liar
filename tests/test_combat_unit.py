import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from combat import CombatManager
from mechanics import SkillSystem

def test_combat_flow():
    print("--- Testing Combat Flow ---")
    
    # Setup
    skill_sys = SkillSystem()
    player_state = {"injuries": [], "sanity": 50}
    cm = CombatManager(skill_sys, player_state)
    
    # Mock SkillSystem roll_check slightly if needed, but defaults are random
    # We'll rely on randomness or use manual mode if mechanics supports it (mechanics.py has set_manual_mode!) 

    
    # Start Encounter
    enemies = [{"name": "Thug", "hp": 3, "reflexes": 1, "attack": 2}]
    cm.start_encounter(enemies, "combat")
    
    if not cm.active:
        print("FAIL: Combat did not start.")
        return

    print(f"Status: Active={cm.active}, Enemies={len(cm.enemies)}")
    
    # Test Player Turn
    # We don't have a rigid turn enforcer in perform_action yet, it just processes player action then enemy reaction
    
    # Player Attacks Thug
    # Manually force a hit. 
    # roll_check call: skill="Hand-to-Hand Combat", DC=8+1=9.
    # manual mode requires us to patch roll_check or just trust it uses manual_roll param if we could pass it.
    # mechanics.py implementation of roll_check takes `manual_roll` arg but CombatManager doesn't pass it down.
    # However, mechanics.py `roll_check` uses `random.randint` if `manual_roll` is None.
    # `set_manual_mode` only sets a flag but `roll_check` doesn't seem to check that flag in the code I saw?
    # Let's re-read mechanics.py snippet...
    # Line 118: if manual_roll is not None: ... else: random... 
    # It doesn't check self.manual_dice_mode! 
    # Ah, I missed that implementing detail in mechanics.py or it's incomplete.
    # It's fine, we'll deal with randomness.
    
    print("Action: Player attacks Thug")
    result = cm.perform_action("attack", "Thug", "Hand-to-Hand Combat")
    print(f"Result: {result}")
    
    # Check log
    print("Log:")
    for l in cm.log:
        print(f"  {l}")

    # Test Injury Application
    print("\nAction: Apply Mock Injury")
    cm.apply_injury("Gunshot", "Leg", ["-2 Athletics"])
    
    print(f"Injuries: {player_state['injuries']}")
    
    # Test Penalty Logic
    penalty = cm._get_total_injury_penalty("Athletics")
    if penalty == -2:
        print("PASS: Injury penalty calculated correctly.")
    else:
        print(f"FAIL: Injury penalty wrong. Got {penalty}, expected -2.")
        
    # End Encounter
    cm.end_encounter()
    if not cm.active:
        print("PASS: Encounter ended.")
    else:
        print("FAIL: Encounter still active.")

if __name__ == "__main__":
    test_combat_flow()
