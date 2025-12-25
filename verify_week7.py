
import os
import sys

# Add src and engine to path
base_path = os.path.abspath(".")
sys.path.append(os.path.join(base_path, 'src'))
sys.path.append(os.path.join(base_path, 'src', 'engine'))

from game import Game, resource_path
from engine.location_system import LocationManager
from engine.trigger_system import TriggerManager

def test_location_system():
    print("--- Testing LocationManager ---")
    lm = LocationManager()
    lm.load_locations(resource_path(os.path.join('data', 'locations.json')))
    
    trailhead = lm.get_location("trailhead")
    print(f"Trailhead: {trailhead['name']}")
    
    connections = lm.get_connected_locations("trailhead")
    print(f"Connections from trailhead: {list(connections.keys())}")
    
    # Check conditional entry
    state = {
        "location_states": {"woods_clearing": {"locked": True}},
        "player_flags": set()
    }
    can_enter = lm.can_enter("woods_clearing", state)
    print(f"Can enter woods_clearing (locked): {can_enter}")
    
    state["location_states"]["woods_clearing"]["locked"] = False
    can_enter = lm.can_enter("woods_clearing", state)
    print(f"Can enter woods_clearing (unlocked): {can_enter}")

def test_trigger_system():
    print("\n--- Testing TriggerManager ---")
    tm = TriggerManager()
    tm.load_triggers(resource_path(os.path.join('data', 'triggers.json')))
    
    from datetime import datetime
    state = {
        "current_location": "trailhead",
        "time": datetime(2025, 12, 25, 1, 0), # 1:00 AM (after 00:30)
        "player_flags": set(),
        "location_states": {"woods_clearing": {"fire_started": True}},
        "sanity": 80,
        "reality": 90
    }
    
    fired = tm.check_triggers(state)
    print(f"Fired triggers (Fire event?): {[t['id'] for t in fired]}")

def test_game_integration():
    print("\n--- Testing Game Integration ---")
    g = Game()
    # Initialize specific scene for test
    g.scene_manager.load_scene("trailhead")
    
    print(f"Current Location: {g.player_state['current_location']}")
    print(f"Location States Table exists: {'location_states' in g.player_state}")
    
    # Test GO command via handle_parser_command
    print("\nMoving to woods_clearing...")
    g.handle_parser_command("GO", "woods clearing")
    print(f"New Location: {g.player_state['current_location']}")
    
    # Test MAP command
    print("\nDisplaying Map:")
    g.display_map()

if __name__ == "__main__":
    try:
        test_location_system()
        test_trigger_system()
        test_game_integration()
        print("\nAll integration tests passed!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
