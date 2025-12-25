import sys
import os

# quick hack to add root to path
sys.path.append(os.getcwd())

from player.game_state import GameState
from engine.combat_system import start_combat, resolve_turn, enemy_turn, ENEMIES
from engine.injury_system import apply_injury, heal_injury

def test_combat_flow():
    print("=== TESTING COMBAT FLOW ===")
    state = GameState()
    
    # 1. Initialize Combat
    print("\n[Test 1] Start Combat")
    start_combat(state, "unknown_assailant")
    assert state.combat_state is not None
    assert state.combat_state["enemy_id"] == "unknown_assailant"
    print("PASS: Combat initialized.")

    # 2. Player Fight
    print("\n[Test 2] Player Fight Action")
    # cheat skills to ensure hit
    state.skills["Hand-to-Hand Combat"] = 6 
    
    initial_hp = state.combat_state["hp"]
    outcome = resolve_turn(state, "fight")
    new_hp = state.combat_state["hp"]
    
    print(f"Enemy HP: {initial_hp} -> {new_hp}")
    assert new_hp < initial_hp
    print("PASS: Player dealt damage.")

    # 3. Enemy Turn (and Dodge)
    print("\n[Test 3] Player Dodge & Enemy Attack")
    state.skills["Reflexes"] = 10 # Ensure success
    outcome = resolve_turn(state, "dodge")
    assert state.combat_state["dodging"] == True
    
    # AI Attack (should miss due to dodge)
    enemy_turn(state)
    assert not state.injuries # Should be no injury if dodged
    assert state.combat_state["dodging"] == False # Dodge consumed
    print("PASS: Dodge worked.")

    # 4. Player Injury
    print("\n[Test 4] Forced Injury")
    # Reset dodge just in case
    state.combat_state["dodging"] = False
    # Manually injure
    apply_injury(state, "leg", "minor")
    assert len(state.injuries) == 1
    assert state.injuries[0]["location"] == "leg"
    print("PASS: Injury applied.")

    # 5. Collapse Check
    print("\n[Test 5] Systemic Collapse")
    # Add critical injuries
    apply_injury(state, "head", "severe")
    apply_injury(state, "torso", "critical")
    # Now loop injury logic triggers collapse?
    # Our simple implementaion only checks during 'apply_injury' or 'check_trauma'
    # We called apply_injury, so it should have warned.
    
    print("State Injuries:", len(state.injuries))
    # Let's force a collapse via heal if logic was there, or just call handle_systemic_collapse
    from engine.injury_system import handle_systemic_collapse
    handle_systemic_collapse(state)
    
    assert state.current_scene == "hospital_recovery"
    assert len(state.injuries) == 0 # Cleared on collapse
    print("PASS: Collapsed to Hospital.")

    print("\n=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    test_combat_flow()
