import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from combat import CombatManager
from mechanics import SkillSystem

def test_combat_flow():
    print("--- Testing Combat Flow ---")
    
    # Setup
    skill_sys = SkillSystem()
    player_state = {"injuries": [], "sanity": 50}
    cm = CombatManager(skill_sys, player_state)
    
    # Start Encounter
    enemies = [{"name": "Thug", "hp": 3, "reflexes": 1, "attack": 2}]
    cm.start_encounter(enemies, "combat")
    
    if not cm.active:
        print("FAIL: Combat did not start.")
        sys.exit(1)

    print(f"Status: Active={cm.active}, Enemies={len(cm.enemies)}")
    
    # --- Test Player Attack (Forced Hit) ---
    # Target Reflexes is 1, so DC = 8 + 1 = 9.
    # Player Hand-to-Hand base is usually 0 or 1.
    # Force roll of 10. Total 10 > 9. Should Hit.
    print("\nAction: Player attacks Thug (Forced Hit)")
    result = cm.perform_action("attack", "Thug", "Hand-to-Hand Combat", manual_roll=10)
    print(f"Result: {result}")
    
    # Verify Hit
    thug = cm._get_enemy_by_name("Thug")
    if thug["hp"] < 3:
        print("PASS: Thug took damage.")
    else:
        print(f"FAIL: Thug HP did not decrease. HP: {thug['hp']}")
        sys.exit(1)

    # --- Test Player Attack (Forced Miss) ---
    # Force roll of 2. Total 2 < 9. Should Miss.
    print("\nAction: Player attacks Thug (Forced Miss)")
    result = cm.perform_action("attack", "Thug", "Hand-to-Hand Combat", manual_roll=2)
    print(f"Result: {result}")
    
    if "Missed" in result:
        print("PASS: Attack missed as expected.")
    else:
        print(f"FAIL: Expected miss, got: {result}")

    # --- Test Injury Application & Penalty ---
    print("\nAction: Apply Mock Injury")
    cm.apply_injury("Gunshot", "Leg", ["-2 Athletics"])
    
    # Verify key consistency (healing_time_remaining)
    injury = player_state["injuries"][0]
    print(f"Injury keys: {injury.keys()}")
    if "healing_time_remaining" in injury and injury["healing_time_remaining"] == 72 * 60:
         print("PASS: Injury has correct 'healing_time_remaining' key and value (minutes).")
    else:
         print(f"FAIL: Injury key/value incorrect: {injury}")

    # Test Penalty Logic
    penalty = cm._get_total_injury_penalty("Athletics")
    if penalty == -2:
        print("PASS: Injury penalty calculated correctly.")
    else:
        print(f"FAIL: Injury penalty wrong. Got {penalty}, expected -2.")
        
    # --- Test Flee (Forced Success) ---
    # DC 10. Force roll 11.
    print("\nAction: Flee (Forced Success)")
    result = cm.perform_action("flee", manual_roll=11)
    print(f"Result: {result}")

    if not cm.active:
        print("PASS: Encounter ended after flee.")
    else:
        print("FAIL: Encounter still active.")

if __name__ == "__main__":
    test_combat_flow()
