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
    game.skill_system.get_skill("Composure").base_level = 5
    game.skill_system.attributes["REASON"].value = 1
    game.skill_system.attributes["INTUITION"].value = 1
    
    for scene_id in scenes_flow:
        print(f"\n{Colors.CYAN}>>> LOADING: {scene_id}{Colors.ENDC}")
        game.scene_manager.load_scene(scene_id)
        
        # Capture description using the same logic as Game.display_scene
        current_lens = game.lens_system.calculate_lens()
        archetype_map = {
            "believer": "believer", "skeptic": "skeptic", "haunted": "haunted"
        }
        from engine.text_composer import Archetype
        arch_obj_map = {
            "believer": Archetype.BELIEVER,
            "skeptic": Archetype.SKEPTIC,
            "haunted": Archetype.HAUNTED
        }
        archetype = arch_obj_map.get(current_lens, Archetype.NEUTRAL)
        
        scene = game.scene_manager.current_scene_data
        text_data = scene.get("text", {"base": "..."})
        if isinstance(text_data, str):
            text_data = {"base": text_data}
            
        composed = game.text_composer.compose(text_data, archetype, game.player_state)
        desc = composed.full_text
        print(f"{Colors.GREEN}LENS: {current_lens.upper()}{Colors.ENDC}")
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

    # 3. Verify Dialogue Branching (Maude)
    print(f"\n{Colors.CYAN}>>> TESTING DIALOGUE: maude_checkin (HAUNTED){Colors.ENDC}")
    dialogues_dir = os.path.join(os.getcwd(), "data", "dialogues")
    game.dialogue_manager.load_dialogue("maude_checkin", dialogues_dir)
    
    # Check start node (maude_greet HAS a lens, so no (familiar) expected)
    render_data = game.dialogue_manager.get_render_data()
    print(f"{Colors.GREEN}SPEAKER (Node 1):{Colors.ENDC} {render_data['speaker']}")
    
    # Test Branching: Choice 3 (indexed as "3" in input) is Haunted exclusive
    print("[DEBUG] Selecting Haunted Choice (3)...")
    game.dialogue_manager.process_input("3")
    
    # Check second node (maude_fire_shared HAS NO lens, so (familiar) IS expected)
    render_data_2 = game.dialogue_manager.get_render_data()
    print(f"{Colors.GREEN}SPEAKER (Node 2):{Colors.ENDC} {render_data_2['speaker']}")
    print(f"{Colors.GREEN}TEXT:{Colors.ENDC} {render_data_2['text'][:100]}...")
    
    if "(familiar)" in render_data_2['speaker'] and game.dialogue_manager.current_node_id == "maude_fire_shared":
        print("[PASS] Haunted Dialogue Branching & Modulation verified.")
    else:
        print(f"{Colors.FAIL}[FAIL] Haunted Verification failed! Node: {game.dialogue_manager.current_node_id}, Speaker: {render_data_2['speaker']}{Colors.ENDC}")

    print("\n=== PLAYTEST COMPLETE ===")

if __name__ == "__main__":
    run_playtest()
