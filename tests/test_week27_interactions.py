
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'engine'))

from game import Game
from inventory_system import Item

def test_interactions():
    print("--- STARTING INTERACTION TEST ---")
    game = Game()

    # Load test scene
    print("Loading test scene...")
    # scene ID in json is "test_interaction_room", but filename is "test_interaction.json"
    # scene_manager loads by ID inside the file.
    scene = game.scene_manager.load_scene("test_interaction_room")
    if not scene:
        print("ERROR: Could not load test_interaction_room scene.")
        return

    # 1. Test Collect
    print("\n--- TEST: COLLECT TOOLS ---")
    game.handle_parser_command("COLLECT", "forensics kit")
    game.handle_parser_command("COLLECT", "uv light")
    game.handle_parser_command("COLLECT", "flashlight")

    # Verify inventory
    inv_names = [i.name for i in game.inventory_system.carried_items]
    print(f"Inventory: {inv_names}")
    assert "Forensics Kit" in inv_names
    assert "UV Light" in inv_names
    assert "Flashlight" in inv_names

    # 2. Test Flashlight on Dark Corner
    print("\n--- TEST: FLASHLIGHT INTERACTION ---")
    # "shine" is mapped to flashlight in game.py logic for "dark" objects
    # But let's try explicit "USE FLASHLIGHT ON DARK CORNER" first if parser supports it
    # game.handle_parser_command("USE", "flashlight on dark_corner")
    # Actually my parser logic in game.py handles "USE <TOOL> ON <TARGET>"

    game.process_command("use flashlight on dark corner", [])

    # Check if object state changed (description should change)
    obj = game.scene_manager.current_scene_data["objects"]["dark_corner"]
    print(f"Dark Corner Status: {obj['name']}")
    assert obj["name"] == "Exposed Safe"

    # 3. Test UV Light
    print("\n--- TEST: UV LIGHT INTERACTION ---")
    game.process_command("use uv light on blood stain", [])

    # 4. Test Swab (Verb)
    print("\n--- TEST: SWAB VERB ---")
    game.process_command("swab blood stain", [])

    # Verify Evidence
    ev_ids = list(game.inventory_system.evidence_collection.keys())
    print(f"Evidence Collected: {ev_ids}")
    assert any("blood_sample" in eid for eid in ev_ids)

    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_interactions()
