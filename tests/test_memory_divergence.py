import sys
import os

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'src'))

from engine.flashback_system import FlashbackManager
from engine.scene_manager import SceneManager
# Mock other dependencies
class MockSystem:
    def __init__(self):
        self.skills = {}
    def to_dict(self): return {}
    def load_state_from_dict(self, d): pass

def test_memory_divergence():
    print("=== TESTING MEMORY DIVERGENCE ===")
    
    # Setup
    player_state = {"sanity": 100}
    skill_system = MockSystem()
    flashback_manager = FlashbackManager(skill_system, player_state)
    
    # Mock Scene Data
    memory_scene = {
        "id": "test_memory",
        "type": "memory",
        "text": {
            "objective": "OBJECTIVE_TEXT",
            "traumatic": "TRAUMATIC_TEXT"
        }
    }
    
    # 1. High Sanity Test (Objective)
    print("\n[TEST 1] High Sanity (100)")
    player_state["sanity"] = 100
    text = flashback_manager.get_memory_text(memory_scene)
    print(f"Retrieved: {text}")
    assert text == "OBJECTIVE_TEXT", "Should return objective text at high sanity"
    
    # 2. Low Sanity Test (Traumatic)
    print("\n[TEST 2] Low Sanity (20)")
    player_state["sanity"] = 20
    text = flashback_manager.get_memory_text(memory_scene)
    print(f"Retrieved: {text}")
    assert text == "TRAUMATIC_TEXT", "Should return traumatic text at low sanity"
    
    # 3. Mid Sanity Test (Boundary)
    print("\n[TEST 3] Mid Sanity (49)")
    player_state["sanity"] = 49
    text = flashback_manager.get_memory_text(memory_scene)
    print(f"Retrieved: {text}")
    assert text == "TRAUMATIC_TEXT", "Sanity < 50 should be traumatic"
    
    print("\n[TEST 4] Mid Sanity (50)")
    player_state["sanity"] = 50
    text = flashback_manager.get_memory_text(memory_scene)
    print(f"Retrieved: {text}")
    assert text == "OBJECTIVE_TEXT", "Sanity >= 50 should be objective"

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_memory_divergence()
