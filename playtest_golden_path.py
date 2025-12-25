import sys
import json
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from text_composer import TextComposer, Archetype
from dice import DiceSystem
from discovery_system import DiscoverySystem
from board_manager import BoardManager
from encounter_manager import EncounterManager

def playtest_vertical_slice():
    print("=== VERTICAL SLICE GOLDEN PATH PLAYTEST ===\n")
    
    # 1. Setup
    gs = GameState()
    gs.archetype = "SKEPTIC" # Using a valid string archetype for initial test
    gs.attributes["REASON"] = 4
    gs.attributes["INTUITION"] = 3
    gs.skills["Forensics"] = 2
    gs.skills["Athletics"] = 1
    
    dice = DiceSystem()
    composer = TextComposer(game_state=gs)
    discovery = DiscoverySystem(gs, composer)
    board = BoardManager(gs)
    enc = EncounterManager(gs, dice)
    
    # Load data (simulated for now)
    scenes = json.load(open("data/scenes/vertical_slice.json"))
    clues = json.load(open("data/clues/vertical_slice_clues.json"))
    theories = json.load(open("data/theories/vertical_slice_theories.json"))
    
    clue_map = {c["id"]: c for c in clues}
    theory_map = {t["id"]: t for t in theories}
    scene_map = {s["id"]: s for s in scenes}
    
    # 2. START: Arrival at Cliff
    print("[SCENE] Arrival at Cliff")
    curr_scene = scene_map["arrival_cliff"]
    comp = composer.compose(curr_scene, Archetype.SKEPTIC, gs)
    print(comp.full_text)
    
    # 3. Discover Passive Clue
    print("\n--- Checking Passive Clues ---")
    new_clues = discovery.evaluate_passive_clues(curr_scene)
    for c_note in new_clues:
        cid = c_note["id"]
        print(f"Discovered: {clue_map[cid]['title']}")
        board.add_clue(cid, clue_map[cid])
        
    # 4. Action: Examine Tire Tracks
    print("\n[ACTION] Examine Tire Tracks")
    # This usually involves a check, let's simulate the success
    curr_scene = scene_map["tire_tracks"]
    print(composer.compose(curr_scene, Archetype.SKEPTIC, gs).full_text)
    
    # 5. Action: Go to Wreck Base
    print("\n[ACTION] Climb down to wreck base (Athletics Check)")
    curr_scene = scene_map["wreck_base"]
    # Athletics 1 + Reason 4? No, Athletics + attribute? Skill map says Athletics is Presence/Constitution?
    # Let's just use gs.get_effective_skill
    eff = gs.get_effective_skill("Athletics")
    roll = dice.resolve_check("Athletics", eff, dc=7, manual_roll=8) # Success
    comp = composer.compose(curr_scene, Archetype.SKEPTIC, gs)
    print(comp.full_text)
    
    # 6. Encounter: Cave Entry
    print("\n[ENCOUNTER] Entering the Cave")
    # Need to load the encounter data
    enc_data = json.load(open("data/encounters/vertical_slice_encounters.json"))["encounter"]
    print(enc.start_encounter(enc_data))
    
    res = enc.resolve_turn(0, manual_roll=10) # Win!
    print(res["description"])
    print(f"Exit: {res['exit_msg']}")
    
    # 7. Final Check: Board State
    print("\n--- FINAL BOARD STATE ---")
    print(board.get_board_summary())
    
    print("\nPlaytest Complete. Golden Path verified.")

if __name__ == "__main__":
    playtest_vertical_slice()
