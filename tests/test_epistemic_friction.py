import sys
import os
import time

# Add project root and src/engine to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(root_dir, 'src'))
sys.path.append(os.path.join(root_dir, 'src', 'engine'))

from engine.board import Board
from engine.psychological_system import PsychologicalState

def test_epistemic_friction():
    print("=== TESTING EPISTEMIC FRICTION ===")
    
    # 1. Setup Board
    board = Board()
    
    # Ensure we have conflicting theories available
    # "Trust No One" conflicts with "Protect The Innocent"
    t1 = "trust_no_one"
    t2 = "protect_innocent"
    
    # Force unlock them for testing
    board.discover_theory(t1)
    board.discover_theory(t2)
    
    print(f"Theories unlocked: {t1}, {t2}")
    
    # 2. Internalize First Theory
    print(f"\nInternalizing {t1}...")
    success = board.start_internalizing(t1)
    if success:
        # Fast forward internalization
        board.on_time_passed(600) # 10 hours
        print(f"Status of {t1}: {board.get_theory(t1).status}")
    
    # 3. Try to Internalize Conflicting Theory (Normal)
    print(f"\nAttempting to internalize {t2} (Normal)...")
    success = board.start_internalizing(t2)
    print(f"Success? {success}") # Should be False
    
    # 4. Force Internalize Conflicting Theory
    print(f"\nAttempting to internalize {t2} (Forced)...")
    success = board.start_internalizing(t2, force=True)
    print(f"Success? {success}") # Should be True
    
    if success:
        friction = board.get_theory(t2).friction_level
        print(f"Friction Level for {t2}: {friction}")
        assert friction > 0, "Friction should be set > 0"
        
        # Fast forward
        board.on_time_passed(600)
        print(f"Status of {t2}: {board.get_theory(t2).status}")
        
    # 5. Verify Total Friction
    total_friction = board.get_total_friction()
    print(f"\nTotal Board Friction: {total_friction}")
    assert total_friction > 0, "Total friction should be positive"
    
    # 6. Test Game Loop Integration (Mental Load)
    # Mocking the loop part logic
    print("\nSimulating Game Loop Time Pass...")
    player_state = {"mental_load": 0, "sanity": 100}
    psych = PsychologicalState(player_state)
    
    # Simulate 1 hour (60 mins)
    minutes = 60
    friction_load = (total_friction / 60.0) * minutes
    psych.add_mental_load(int(friction_load), "Epistemic Friction")
    
    print(f"Mental Load after 1 hour: {player_state['mental_load']}")
    assert player_state['mental_load'] > 0, "Mental Load should have increased"

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_epistemic_friction()
