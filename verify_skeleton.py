import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from game import Game

def test_skeleton():
    print("Testing Project Skeleton...")
    try:
        game = Game()
        output = game.start_game(start_scene_id="hello")
        print("\n--- Game Output ---")
        print(output)
        print("-------------------\n")
        
        state = game.get_ui_state()
        print(f"Current Location: {state['location']}")
        print(f"Sanity: {state['sanity']}")
        
        if "Welcome to Tyger Tyger Liar Liar" in output:
            print("\n[SUCCESS] Skeleton is running and scene loaded correctly.")
        else:
            print("\n[FAILURE] Scene text not found in output.")
            
    except Exception as e:
        print(f"\n[ERROR] Skeleton failed to run: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skeleton()
