
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mechanics import SkillSystem
from core_game import Game

def test_psychology():
    print("--- TESTING PSYCHOLOGY SYSTEM ---")
    g = Game()
    
    print(f"\nInitial State: Sanity={g.player_state['sanity']}, Reality={g.player_state['reality']}")
    
    # 1. Test Reality Distortion
    g.player_state["reality"] = 40
    distorted = g.apply_reality_distortion("The door and the window are closed.")
    print(f"\nReality 40 distortion test:")
    print(f"Original: 'The door and the window are closed.'")
    print(f"Distorted: '{distorted}'")
    
    # 2. Test Passive Interrupts with low sanity
    g.player_state["sanity"] = 20
    # Boost some skills to see interjections
    g.skill_system.get_skill("Logic").base_level = 3
    g.skill_system.get_skill("Skepticism").base_level = 3
    
    print(f"\nSanity 20 interrupt test:")
    interrupts = g.skill_system.check_passive_interrupts("the strange mirror", g.player_state["sanity"])
    for msg in interrupts:
        print(f" > {msg}")
    
    # 3. Test Scene Entry Effects
    print(f"\nTesting 'mirror_hall' entry effects:")
    # Reset sanity/reality
    g.player_state["sanity"] = 100
    g.player_state["reality"] = 100
    
    g.scene_manager.load_scene("mirror_hall")
    print(f"After entering 'mirror_hall': Sanity={g.player_state['sanity']}, Reality={g.player_state['reality']}")
    
    if g.player_state["reality"] == 70:
        print("✓ Reality entry effect correctly applied (-30).")
    else:
        print(f"✗ Reality entry effect failure: Expected 70, got {g.player_state['reality']}")

    # 4. Test Ambient Drain
    print(f"\nTesting ambient drain (10 minutes in mirror_hall):")
    g.on_time_passed(10)
    # Expected san drain: 0.5 * 10 = 5
    if g.player_state["sanity"] == 95:
        print("✓ Ambient sanity drain correctly applied (-5).")
    else:
        print(f"✗ Ambient sanity drain failure: Expected 95, got {g.player_state['sanity']}")

if __name__ == "__main__":
    test_psychology()
