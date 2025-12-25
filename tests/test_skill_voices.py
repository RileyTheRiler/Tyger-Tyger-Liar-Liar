import sys
import os

# Add project root and src/engine to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'src'))
sys.path.append(os.path.join(root_dir, 'src', 'engine'))

from engine.text_composer import TextComposer, Archetype
from mechanics import SkillSystem
from engine.psychological_system import PsychologicalState

def test_skill_voices():
    print("=== TESTING SKILL VOICES SYSTEM ===")
    
    # Setup
    skill_system = SkillSystem()
    # Boost some skills to trigger passive checks
    skill_system.get_skill("Logic").base_level = 6
    skill_system.get_skill("Paranormal Sensitivity").base_level = 6
    skill_system.get_skill("Authority").base_level = 6
    
    player_state = {
        "sanity": 100,
        "active_theories": [],
        "flags": set()
    }
    
    composer = TextComposer(skill_system=skill_system, game_state=player_state)
    composer.debug_mode = True
    
    scene_data = {
        "id": "test_scene",
        "text": {
            "base": "You stand in the middle of the old library. The shelves are heavy with dust and silence."
        }
    }
    
    # 1. Test Stable Sanity (Tier 4)
    print("\n--- TEST 1: STABLE SANITY (Tier 4) ---")
    composed = composer.compose(scene_data, archetype=Archetype.NEUTRAL, player_state=player_state)
    print(composed.full_text)
    
    # 2. Test Low Sanity (Tier 1)
    print("\n--- TEST 2: LOW SANITY (Tier 1) ---")
    player_state["sanity"] = 15
    composed = composer.compose(scene_data, archetype=Archetype.NEUTRAL, player_state=player_state)
    print(composed.full_text)
    
    # 3. Test Breakdown (Tier 0)
    print("\n--- TEST 3: BREAKDOWN (Tier 0) ---")
    player_state["sanity"] = 5
    composed = composer.compose(scene_data, archetype=Archetype.NEUTRAL, player_state=player_state)
    print(composed.full_text)

if __name__ == "__main__":
    test_skill_voices()
