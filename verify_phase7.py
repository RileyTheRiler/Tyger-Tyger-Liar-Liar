import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from dice import DiceSystem
from encounter_manager import EncounterManager

def verify_phase7():
    print("Verifying Phase 7: Encounters v1...")
    
    gs = GameState()
    dice = DiceSystem()
    enc = EncounterManager(gs, dice)
    
    test_encounter = {
        "id": "frozen_pass",
        "intro_text": {"base": "The wind howls. You must find shelter before the cold takes you."},
        "state_defaults": {"progress": 0, "warmth": 100},
        "turn_rules": {"warmth": -30}, # Lose 30 warmth per turn
        "options_by_turn": [
            [ # Turn 1
                {
                    "label": "Push through the snow",
                    "skill": "Athletics",
                    "dc": 7,
                    "outcomes": {
                        "success": {"text": "You make good progress.", "effects": {"progress": 3}},
                        "failure": {"text": "The snow is too deep.", "effects": {"progress": 1}}
                    }
                }
            ],
            [ # Turn 2
                {
                    "label": "Look for a cave",
                    "skill": "Perception",
                    "dc": 9,
                    "outcomes": {
                        "success": {"text": "You find a small cave!", "effects": {"progress": 5}},
                        "failure": {"text": "Nothing but white out.", "effects": {"progress": 1}}
                    }
                }
            ]
        ],
        "exit_conditions": {
            "success": {"state_gte": {"progress": 5}, "text": "You found shelter!"},
            "failure": {"state_lte": {"warmth": 0}, "text": "The cold has won."}
        }
    }
    
    print("\nStarting Encounter...")
    print(enc.start_encounter(test_encounter))
    
    # Turn 1
    print("\n--- Turn 1 ---")
    res1 = enc.resolve_turn(0, manual_roll=7) # Success
    print(res1["description"])
    print(f"State: {res1['encounter_state']}")
    
    # Turn 2
    print("\n--- Turn 2 ---")
    res2 = enc.resolve_turn(0, manual_roll=9) # Success
    print(res2["description"])
    print(f"State: {res2['encounter_state']}")
    print(f"Exit Msg: {res2['exit_msg']}, Finished: {res2['finished']}")
    
    if res2["finished"] and "found shelter" in res2["exit_msg"].lower():
        print("\n[SUCCESS] Encounter loop and success exit verified.")
    else:
        print("\n[FAILURE] Encounter did not finish as expected.")

if __name__ == "__main__":
    verify_phase7()
