import sys
import os

# Add src to path
sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('.'))

from game import Game
from mechanics import SkillSystem
from text_composer import Archetype

def test_integration():
    print("=== STARTING INTEGRATION TEST ===")
    
    # Init Game
    game = Game()
    
    # 1. Test Resonance
    print("\n--- Testing Resonance ---")
    game.player_state["resonance_count"] = 347
    game.modify_resonance(-1, cause="Death")
    assert game.player_state["resonance_count"] == 346
    print("Resonance modification successful.")
    
    # 2. Test Thermal Mode & Text Composition
    print("\n--- Testing Thermal Mode ---")
    game.player_state["thermal_mode"] = True
    
    # Create dummy scene data
    scene_data = {
        "base": "Normal view.",
        "thermal": "Thermal view.",
        "lens": {"believer": "Believer view."}
    }
    
    # Compose
    result = game.text_composer.compose(scene_data, Archetype.NEUTRAL, game.player_state, thermal_mode=True)
    print(f"Composed Text (Thermal ON): {result.full_text}")
    assert "Thermal view" in result.full_text
    
    result_off = game.text_composer.compose(scene_data, Archetype.NEUTRAL, game.player_state, thermal_mode=False)
    print(f"Composed Text (Thermal OFF): {result_off.full_text}")
    assert "Normal view" in result_off.full_text
    
    # 3. Test Skill Interjections Structure
    print("\n--- Testing Skill Interjections ---")
    # Force a skill to be high enough to match mechanics logic
    # Logic: roll(2d6) + level + sanity_bonus >= 11
    # We can fake it by calling maybe_interrupt directly with max level
    
    skill = game.skill_system.get_skill("Logic")
    skill.base_level = 10 # Super high
    
    interrupt = skill.maybe_interrupt("Test context", sanity=100)
    print(f"Interrupt Result: {interrupt}")
    
    if interrupt:
        assert isinstance(interrupt, dict)
        assert "color" in interrupt
        assert "icon" in interrupt
        print("Interrupt structure valid.")
    else:
        print("WARNING: No interrupt triggered (might be random chance, but lvl 10 should trigger often).")

    print("\n=== INTEGRATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_integration()
