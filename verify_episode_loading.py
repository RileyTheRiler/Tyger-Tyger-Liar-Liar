import sys
import unittest
import json
import os
import shutil

# Ensure paths are set up before importing game
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

# Pre-import to avoid potential circular dependency issues during test
import inventory_system
from game import Game

class TestEpisodeLoading(unittest.TestCase):
    def setUp(self):
        # Create a test episode directory
        self.test_episode_name = "test_episode_verification"
        self.episodes_dir = os.path.join(os.getcwd(), "episodes")
        self.test_episode_path = os.path.join(self.episodes_dir, self.test_episode_name)
        
        if os.path.exists(self.test_episode_path):
            shutil.rmtree(self.test_episode_path)
        
        # Copy 'data' to 'episodes/test_verification'
        # We need a full copy because Game loads EVERYTHING
        src_data = os.path.join(os.getcwd(), "data")
        shutil.copytree(src_data, self.test_episode_path)
        
        # Modify scenes.json to have a unique identifier
        scenes_path = os.path.join(self.test_episode_path, "scenes.json")
        with open(scenes_path, 'r') as f:
            scenes = json.load(f)
            
        # Modify the first scene text
        if scenes:
            scenes[0]['text'] = "VERIFICATION_UNIQUE_STRING: This is the test episode."
            
        with open(scenes_path, 'w') as f:
            json.dump(scenes, f, indent=2)
            
    def tearDown(self):
        # Clean up
        if os.path.exists(self.test_episode_path):
            try:
                shutil.rmtree(self.test_episode_path)
            except PermissionError:
                print(f"Warning: Could not delete {self.test_episode_path} - file in use?")

    def test_load_custom_episode(self):
        print("\nTesting loading of custom episode...")
        
        # Initialize Game with explicit content root
        # We bypass config loading logic by passing the argument directly
        game = Game(content_root=self.test_episode_path)
        
        # Start game output
        output = game.start_game()
        
        # Check for unique string
        print(f"Game Output Start: {output[:100]}...")
        
        self.assertIn("VERIFICATION_UNIQUE_STRING", output)
        print("SUCCESS: Custom episode loaded correctly.")

if __name__ == "__main__":
    unittest.main()
