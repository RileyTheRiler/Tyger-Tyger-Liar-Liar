import sys
import os
import shutil
import json

# Setup paths closely mimicking what works in debug_import
root_dir = os.getcwd()
sys.path.append(os.path.join(root_dir, "src"))
sys.path.append(os.path.join(root_dir, "src", "engine"))

print("Importing modules in order...")
try:
    import mechanics
    import inventory_system
    import game
    print("Game imported successfully.")
except ImportError as e:
    print("FAILED to import game:", e)
    sys.exit(1)

# Setup Test Episode
test_episode_name = "manual_test_ep"
test_episode_path = os.path.join(root_dir, "episodes", test_episode_name)

if os.path.exists(test_episode_path):
    shutil.rmtree(test_episode_path)

print(f"Creating test episode at {test_episode_path}...")
shutil.copytree(os.path.join(root_dir, "data"), test_episode_path)

# Modify scene
scenes_json_path = os.path.join(test_episode_path, "scenes.json")
try:
    with open(scenes_json_path, 'r') as f:
        scenes = json.load(f)
    
    scenes[0]['text'] = "MANUAL_VERIFY_SUCCESS: The custom episode loaded."
    
    with open(scenes_json_path, 'w') as f:
        json.dump(scenes, f)
except FileNotFoundError:
    print("Error: scenes.json not found in copy.")
    sys.exit(1)

# Run Game
print("Initializing Game with custom content root...")
g = game.Game(content_root=test_episode_path)
output = g.start_game()

print("-" * 20)
print(output[:100])
print("-" * 20)

if "MANUAL_VERIFY_SUCCESS" in output:
    print("VERIFICATION PASSED")
else:
    print("VERIFICATION FAILED")

# Cleanup
# shutil.rmtree(test_episode_path)
