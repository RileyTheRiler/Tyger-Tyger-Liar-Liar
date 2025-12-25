import sys
import os

# Add src and its subdirectories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'ui')))

from engine.text_composer import TextComposer, Archetype, Colors
from engine.mechanics import SkillSystem
from engine.board import Board
from engine.unreliable_narrator import HallucinationEngine

def test_unified_voices():
    print("=== TESTING UNIFIED SKILL VOICES ===")
    
    # Setup
    skill_system = SkillSystem()
    board = Board()
    hallucination_engine = HallucinationEngine()
    
    # Mock some data
    skill_system.get_skill("Logic").base_level = 5
    skill_system.get_skill("Logic").attribute_ref.value = 6
    
    player_state = {
        "sanity": 100.0,
        "active_theories": ["The Truth Is Out There"],
        "instability": False
    }
    
    # Add a mock theory commentary
    skill_system.theory_commentary["The Truth Is Out There"] = {
        "skill": "Subconscious",
        "text": "The pattern is everywhere. You just have to see it."
    }
    
    composer = TextComposer(skill_system, board, player_state, hallucination_engine)
    composer.debug_mode = True
    
    test_scene = {
        "base": "You are standing in the middle of the crime scene. There is a strange residue on the walls."
    }
    
    # 1. High Sanity Test (Skills + Theories)
    print("\n[TEST 1] High Sanity - Logic & Theory")
    result = composer.compose(test_scene, Archetype.NEUTRAL, player_state)
    print(result.full_text)
    
    # 2. Low Sanity Test (Hallucinations)
    print("\n[TEST 2] Low Sanity - Hallucination (Paranoia)")
    player_state["sanity"] = 10.0
    player_state["instability"] = True
    
    # Note: HallucinationEngine needs some "templates" to return competing voices.
    # For this test, we might see empty if no static data is loaded.
    # But HallucinationEngine has some hardcoded ones for things like 'evidence' or 'clue'.
    
    test_scene_low = {
        "base": "The evidence is right in front of you. A simple clue."
    }
    
    result_low = composer.compose(test_scene_low, Archetype.NEUTRAL, player_state)
    print(result_low.full_text)
    
    # 3. Extreme Low Sanity (Corruption)
    print("\n[TEST 3] Extreme Low Sanity - Voice Corruption")
    player_state["sanity"] = 5.0
    
    result_corruped = composer.compose(test_scene, Archetype.NEUTRAL, player_state)
    print(result_corruped.full_text)
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_unified_voices()
