import json
import os

def load_scene(scene_id):
    """
    Loads a scene JSON file from the data/scenes directory.
    """
    # Use relative path from the project root (kaltvik_game/)
    path = os.path.join("data", "scenes", f"{scene_id}.json")
    
    # If not found relative to current working directory, try to find it relative to this file
    if not os.path.exists(path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "data", "scenes", f"{scene_id}.json")

    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)
