import sys
import os
import time

# Ensure imports work regardless of run location
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("src"))

from game import Game
from tyger_game.utils.constants import Colors

def run_playtest():
    print(f"{Colors.HEADER}=== FULL NARRATIVE LOOP PLAYTEST ==={Colors.ENDC}")
    game = Game()
    
    # 1. Start at Wakeup
    print("\n[DEBUG] Forcing start at 'scene_wakeup'...")
    game.scene_manager.load_scene("scene_wakeup")
    
    # Trace the "Haunted" path (PRESENCE)
    path_actions = [
        ("scene_wakeup", "Crawl to the mirror"), # Choice 1 -> Mirror
        ("scene_mirror_gaze", "I see a Survivor"), # Choice 3 -> Sets PRESENCE +2 -> Haunt Lens
        ("intro_arrival", "Disembark"), # Choice 1 -> Lobby
        ("lobby_interrogation", "Demand a room"), # Choice 1 (Checkin) - Wait, needs to exit to Diner? 
                                                  # Actually intro_arrival exits to... lobby? 
                                                  # Let's check the flow. 
                                                  # Flow: wakeup -> mirror -> intro -> lobby -> ?
    ]
    
    # We will just step through scenes manually via load to verify LENS text
    scenes_flow = [
        "scene_wakeup", 
        "scene_mirror_gaze",
        "intro_arrival", 
        "lobby_interrogation",
        "diner", 
        "trailhead", 
        "radio_tower", 
        "frozen_victim", 
        "entity_manifestation"
    ]
    
    # Mocking the attribute boost usually done by Mirror choice
    print("[DEBUG] Simulating Player Choice: High PRESENCE (Haunted Lens)")
    game.skill_system.attributes["PRESENCE"].value = 5 
    game.skill_system.attributes["REASON"].value = 1
    game.skill_system.attributes["INTUITION"].value = 1
    
    for scene_id in scenes_flow:
        print(f"\n{Colors.CYAN}>>> LOADING: {scene_id}{Colors.ENDC}")
        game.scene_manager.load_scene(scene_id)
        
        # Capture description
        desc = game.scene_manager.get_description(game.skill_system) # Pass system as character
        print(f"{Colors.GREEN}TEXT:{Colors.ENDC} {desc[:100]}...")
        
        # Verify Lens trigger
        if scene_id == "intro_arrival":
            if "nightmare" in desc or "wall you stared at" in desc:
                print("[PASS] Haunted Lens verified in Intro.")
            else:
                print(f"{Colors.FAIL}[FAIL] Haunted Lens MISSING in Intro!{Colors.ENDC}")
                
        elif scene_id == "frozen_victim":
            if "It's him" in desc:
                 print("[PASS] Haunted Lens verified in Frozen Victim.")
            else:
                 print(f"{Colors.FAIL}[FAIL] Haunted Lens MISSING in Frozen Victim!{Colors.ENDC}")

    print("\n=== PLAYTEST COMPLETE ===")

if __name__ == "__main__":
    run_playtest()
