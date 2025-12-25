import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from text_composer import TextComposer
from discovery_system import DiscoverySystem

def verify_phase5():
    print("Verifying Phase 5: Passive Perception + Clue Surfacing...")
    
    gs = GameState()
    gs.attributes["INTUITION"] = 5
    gs.skills["Perception"] = 1 # Total 6
    
    composer = TextComposer(game_state=gs)
    discovery = DiscoverySystem(gs, composer)
    
    test_scene = {
        "id": "lobby",
        "passive_clues": [
            {
                "clue_id": "clue_hidden_safe",
                "visible_when": {"skill_gte": {"Perception": 5}},
                "reveal_style": "inline"
            },
            {
                "clue_id": "clue_blood_spatter",
                "visible_when": {"skill_gte": {"Forensics": 10}}, # Won't meet this
                "reveal_style": "panel"
            }
        ]
    }
    
    print("\n--- Evaluating Passive Clues ---")
    new_clues = discovery.evaluate_passive_clues(test_scene)
    
    print(f"Discovered Clues: {[c['id'] for c in new_clues]}")
    
    if len(new_clues) == 1 and new_clues[0]['id'] == "clue_hidden_safe":
        print("[SUCCESS] Passive clue discovery verified.")
    else:
        print(f"[FAILURE] Expected 1 clue (clue_hidden_safe), got {len(new_clues)}.")

    # Check game state persistence
    if any(n["id"] == "clue_hidden_safe" for n in gs.board_graph["nodes"]):
        print("[SUCCESS] Discovered clue registered in GameState board.")
    else:
        print("[FAILURE] Clue not found in board_graph.")

if __name__ == "__main__":
    verify_phase5()
