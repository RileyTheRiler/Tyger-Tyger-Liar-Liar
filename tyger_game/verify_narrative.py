
import sys
import os

# Add path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tyger_game.engine.scene_manager import SceneManager
from tyger_game.engine.character import Character
from tyger_game.utils.constants import ATTRIBUTES

def verify():
    print("Verifying Narrative Data Load...")
    
    # Setup
    base_path = os.path.dirname(os.path.abspath(__file__)) # tyger_game
    root_path = os.path.dirname(base_path) # Tyger Tyger Liar Liar
    scene_manager = SceneManager(root_path)
    scene_manager.data_path = os.path.join(root_path, "data")
    
    scenes_to_test = [
        "radio_tower",
        "intro_arrival",
        "diner",
        "lobby_interrogation",
        "trailhead",
        "scene_wakeup",
        "scene_mirror_gaze",
        "frozen_victim",
        "entity_manifestation"
    ]
    
    print("\n--- Verifying Core Scene Traversal ---")
    
    for scene_id in scenes_to_test:
        print(f"Testing load: {scene_id} ... ", end="")
        try:
            scene = scene_manager.load_scene(scene_id)
            if scene:
                print("OK")
                
                # Content Check
                if "text" in scene and isinstance(scene["text"], dict) and "lens" in scene["text"]:
                    print(f"  > Lens support confirmed for {scene_id}.")
                    
                    # Specific spot checks
                    if scene_id == "intro_arrival" and "particulate matter" in scene["text"]["lens"]["skeptic"]:
                         print(f"  > Specific text verification passed (Skeptic).")
                    elif scene_id == "lobby_interrogation" and "spider in a cardigan" in scene["text"]["lens"]["believer"]:
                         print(f"  > Specific text verification passed (Believer).")
                    elif scene_id == "trailhead" and "40,000 PSI" in scene["text"]["lens"]["skeptic"]:
                         print(f"  > Specific text verification passed (Skeptic).")
                    elif scene_id == "scene_wakeup" and "Boathouse" in scene["text"]["lens"]["haunted"]:
                         print(f"  > Narrative Polish Verification: 'The Ghost' (Truby) confirmed.")
                    elif scene_id == "scene_mirror_gaze" and "reflection lags" in scene["text"]["lens"]["believer"]:
                         print(f"  > Narrative Polish Verification: 'The Gap' (McKee) confirmed.")
                    elif scene_id == "frozen_victim" and "cultivated" in scene["text"]["lens"]["skeptic"]:
                         print(f"  > Major Encounter Verification: 'The Reveal' confirmed.")
                    elif scene_id == "entity_manifestation" and "hemorrhagic event" in scene["text"]["lens"]["skeptic"]:
                         print(f"  > Major Encounter Verification: 'The Climax' confirmed.")
                         
                else:
                    print(f"  > WARNING: No lens variants found or text format incorrect.")
                    
            else:
                print("FAILED (Returns None)")
        except Exception as e:
            print(f"FAILED (Exception: {e})")
            
    print("\nDone.")
if __name__ == "__main__":
    verify()
