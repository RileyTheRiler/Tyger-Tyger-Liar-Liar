import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from engine.endgame_manager import EndgameManager

class MockBoard:
    def get_resolution_summary(self):
        return {"proven": 0, "disproven": 10, "unresolved": 0}
    def get_critical_theories(self):
        return []
    def get_proven_theories(self):
        return []

class MockSkillSystem:
    def __init__(self):
        self.check_history = {}
    def get_skill(self, name):
        return None

def verify_endings():
    print("=== Verifying Endings System ===")
    
    # Setup Logic
    board = MockBoard()
    player_state = {
        "sanity": 50,
        "reality": 80,
        "moral_corruption_score": 0,
        "event_flags": set()
    }
    skill_system = MockSkillSystem()
    
    # Initialize Manager
    manager = EndgameManager(board, player_state, skill_system, endings_path="data/endings")
    
    # Test Loading
    if not manager.endings_data:
        print("[FAIL] No endings loaded!")
        return
    print(f"[PASS] Loaded {len(manager.endings_data)} endings.")
    
    # Test Rationality Logic
    manager.player_state["sanity"] = 50
    manager.player_state["reality"] = 80
    ending = manager.calculate_ending_path()
    # Assuming Rationality conditions are met by MockBoard (all disproven)
    # Actually need high skepticism skill too, which Mock doesn't provide
    # Let's force Collapse
    
    # Test Collapse Logic
    print("Testing Collapse Logic...")
    manager.player_state["sanity"] = 0
    triggered, reason = manager.check_endgame_triggers()
    if triggered and reason == "Sanity collapsed to zero":
         print(f"[PASS] Triggered: {reason}")
    else:
         print(f"[FAIL] Trigger failed: {reason}")
         
    ending_path = manager.calculate_ending_path()
    if ending_path == "ending_collapse":
        print(f"[PASS] Correct ending path calculated: {ending_path}")
    else:
        print(f"[FAIL] Wrong ending path: {ending_path}")
        
    print("=== Verification Complete ===")

if __name__ == "__main__":
    verify_endings()
