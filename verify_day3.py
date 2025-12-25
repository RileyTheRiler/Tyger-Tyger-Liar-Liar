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

def test_day3():
    print("=== Testing Day 3 Events ===")
    
    # Setup
    time_sys = TimeSystem("1995-10-14 08:00") # Day 1
    pop_sys = PopulationSystem()
    player_state = {"flags": {}, "sanity": 100}
    output = MockOutput()
    
    # Initialize
    sm = StoryManager(time_sys, pop_sys, player_state, output)
    
    # --- Test 1: Triggering Green Pulse ---
    print("\n--- Test 1: Day 3 Event ---")
    # Advance to Day 3, 21:00 (Pre-event)
    time_sys.advance_time((24 * 60 * 2) + (13 * 60)) 
    
    if "day3_green_pulse" in player_state.get("triggered_story_events", []):
        print("FAIL: Pulse triggered too early")
    
    # Advance to Day 3, 22:00 (Trigger)
    time_sys.advance_time(60)
    
    if "day3_green_pulse" in player_state.get("triggered_story_events", []):
        print("✓ Event 'day3_green_pulse' triggered")
    else:
        print("X Event FAILED to trigger")
        
    if time_sys.weather == "aurora_storm":
        print("✓ Weather changed to 'aurora_storm'")
    else:
        print(f"X Weather check failed: {time_sys.weather}")

    # --- Test 2: Woods Contextual Insert ---
    print("\n--- Test 2: Woods Scene Context ---")
    
    # Set the flag manually to simulate Day 2 having happened
    player_state["flags"]["old_tom_missing"] = True
    
    # Basic setup for text composer
    # Use mocks to avoid dependency hell in unit test
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
    with open(os.path.join("data", "scenes", "woods_north_path.json"), "r") as f:
        scene_data = json.load(f)
        
    # Render text
    result = composer.compose(scene_data, archetype=Archetype.NEUTRAL, player_state=player_state)
    
    if "toolbag sits near the treeline" in result.full_text:
        print("✓ Insert 'Old Tom's Toolbag' successfully applied")
    else:
        print("X Insert FAILED. Result text:\n" + result[:200] + "...")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_day3()
