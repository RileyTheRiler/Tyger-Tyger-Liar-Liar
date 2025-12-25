import sys
import os
import datetime

# Add source directories to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from engine.story_manager import StoryManager
from engine.population_system import PopulationSystem
from engine.time_system import TimeSystem
from engine.text_composer import TextComposer, Archetype
from engine.scene_manager import SceneManager
from engine.mechanics import SkillSystem
from engine.board import Board

class MockOutput:
    def print(self, text):
        pass # print(f"[MOCK UI] {text}")

def test_day4():
    print("=== Testing Day 4 Events ===")
    
    # Setup
    time_sys = TimeSystem("1995-10-14 08:00") # Day 1
    pop_sys = PopulationSystem()
    player_state = {"flags": {}, "sanity": 100}
    output = MockOutput()
    
    # Initialize
    sm = StoryManager(time_sys, pop_sys, player_state, output)
    
    # --- Test 1: Triggering The Circle ---
    print("\n--- Test 1: Day 4 Event ---")
    # Advance to Day 4, 13:00 (Pre-event)
    # Day 1 start 08:00
    # +24*3 = Day 4 08:00
    # + 5 hours = 13:00
    time_sys.advance_time((24 * 60 * 3) + (5 * 60)) 
    
    if "day4_birds_found" in player_state.get("triggered_story_events", []):
        print("FAIL: Event triggered too early")
    
    # Advance to Day 4, 14:00 (Trigger)
    time_sys.advance_time(60)
    
    if "day4_birds_found" in player_state.get("triggered_story_events", []):
        print("✓ Event 'day4_birds_found' triggered")
    else:
        print("X Event FAILED to trigger")

    # --- Test 2: Town Square Contextual Insert ---
    print("\n--- Test 2: Town Square Scene Context ---")
    
    # Set the flag manually to simulate Day 4
    player_state["flags"]["day4_birds_found"] = True
    
    # Basic setup for text composer
    # Use mocks to avoid dependency hell
    class MockSkillSystem:
        def get_skill(self, name): return None
        def check_passive_interrupts(self, *args, **kwargs): return []
        
    skill_sys = MockSkillSystem()
    board = Board()
    
    # Ensure player state has necessary keys for TextComposer
    player_state["skills"] = {}
    player_state["population_system"] = None
    
    composer = TextComposer(skill_sys, board, player_state)
    
    # Load scene data directly to mock reading file
    import json
    with open(os.path.join("data", "scenes", "town_square.json"), "r") as f:
        scene_data = json.load(f)
        
    # Render text
    result = composer.compose(scene_data, archetype=Archetype.NEUTRAL, player_state=player_state)
    
    if "birds are still here" in result.full_text:
        print("✓ Insert 'Dead Birds' description successfully applied")
    else:
        print("X Insert FAILED. Result text:\n" + result.full_text[:200] + "...")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_day4()
