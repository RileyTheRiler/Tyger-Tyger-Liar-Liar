
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from engine.mechanics import SkillSystem
import game
from game import Game

def test_psychology():
    print("--- TESTING PSYCHOLOGY SYSTEM ---")
    g = Game()
    
    print(f"\nInitial State: Sanity={g.player_state['sanity']}, Reality={g.player_state['reality']}")
    
    # 2. Test Passive Interrupts with Archetype weighting
    g.player_state["sanity"] = 20
    # Boost REASON skill (Skepticism)
    g.skill_system.get_skill("Skepticism").base_level = 3
    # Boost INTUITION skill (Paranormal Sensitivity)
    g.skill_system.get_skill("Paranormal Sensitivity").base_level = 3
    
    print(f"\nSanity 20 interrupt test (Archetype: SKEPTIC):")
    # As a skeptic, Skepticism (REASON) should have a higher weight
    interrupts = g.skill_system.check_passive_interrupts("the strange mirror", g.player_state["sanity"], current_archetype="skeptic")
    for msg in interrupts:
        if msg.get("type") == "argument":
             print(f" > [ARGUMENT]: {msg['text']}")
        else:
             print(f" > {msg['skill']}: {msg['text']}")
    
    print(f"\nSanity 20 interrupt test (Archetype: BELIEVER):")
    # As a believer, Paranormal Sensitivity (INTUITION) should have a higher weight
    interrupts = g.skill_system.check_passive_interrupts("the strange mirror", g.player_state["sanity"], current_archetype="believer")
    for msg in interrupts:
        if msg.get("type") == "argument":
             print(f" > [ARGUMENT]: {msg['text']}")
        else:
             print(f" > {msg['skill']}: {msg['text']}")
    
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
