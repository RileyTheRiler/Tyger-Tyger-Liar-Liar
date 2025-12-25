import sys
import os
import json

# Add source directories to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from engine.mechanics import SkillSystem
from content.dialogue_manager import DialogueManager
from engine.text_composer import Archetype

class MockBoard:
    def __init__(self):
        self.theories = {}
    def is_theory_active(self, tid):
        return False

def test_cabin():
    print("=== Testing Cabin Interview Upgrade ===")
    
    # Setup
    skill_sys = SkillSystem()
    board = MockBoard()
    player_state = {
        "skills": {"Forensics": 5, "Empathy": 7, "Paranormal Sensitivity": 5},
        "sanity": 80,
        "archetype": Archetype.BELIEVER
    }
    
    # Initialize Manager
    dm = DialogueManager(skill_sys, board, player_state)
    
    # Load Dialogue
    print("Loading cabin_interview...")
    if not dm.load_dialogue("cabin_interview", os.path.join("data", "dialogues")):
        print("FAILED: Could not load dialogue.")
        return

    # Render Start Node
    print("\n--- Node: Start (Archetype: BELIEVER) ---")
    data = dm.get_render_data()
    print(f"Speaker: {data['speaker']}")
    print(f"Text:\n{data['text']}")
    
    # Check for Believer lens text
    if "light catching his lenses isn't right" in data['text']:
        print("✓ Believer lens applied")
    else:
        print("X Believer lens MISSING")

    # Check for Forensics Insert (Forensics=5 >= 4)
    if "mud is red clay" in data['text']:
        print("✓ Forensics insert applied")
    else:
         print("X Forensics insert MISSING")

    # Check for Empathy Insert (Empathy=7 >= 6)
    if "pulse is visible" in data['text']:
        print("✓ Empathy insert applied")
    else:
         print("X Empathy insert MISSING")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_cabin()
