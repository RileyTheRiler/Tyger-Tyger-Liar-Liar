import sys
import os
import datetime

# Add source directories to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from engine.story_manager import StoryManager
from engine.population_system import PopulationSystem
from engine.time_system import TimeSystem

class MockOutput:
    def print(self, text):
        print(f"[MOCK UI] {text}")

def test_story_manager():
    print("=== Testing Story Manager (Day 2) ===")
    
    # Setup
    time_sys = TimeSystem("1995-10-14 08:00") # Day 1
    pop_sys = PopulationSystem()
    player_state = {"flags": {}}
    output = MockOutput()
    
    # Initialize
    sm = StoryManager(time_sys, pop_sys, player_state, output)
    
    print(f"Initial Population: {pop_sys.population}")
    
    # Advance to Day 2, 08:00 (Nothing should happen)
    print("\n--- Advancing to Day 2, 08:00 ---")
    time_sys.advance_time(24 * 60) # +24 hours
    
    if "old_tom_missing" in player_state["flags"]:
        print("FAIL: Event triggered too early")
    else:
        print("PASS: Event correctly waiting")

    # Advance to Day 2, 09:00 (Trigger Time)
    print("\n--- Advancing to Day 2, 09:00 ---")
    time_sys.advance_time(60) # +1 hour
    
    # Check Flags
    if player_state["flags"].get("old_tom_missing"):
        print("✓ Flag 'old_tom_missing' SET")
    else:
        print("X Flag 'old_tom_missing' NOT SET")
        
    # Check Population
    if pop_sys.population == 346:
        print("✓ Population DECREASED to 346")
    else:
         print(f"X Population Error: {pop_sys.population}")

    # Check Events
    events = pop_sys.events
    if events and events[-1].npc_id == "npc_old_tom":
        print("✓ Disappearance Event RECORDED")
    else:
        print("X No Disappearance Event found")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_story_manager()
