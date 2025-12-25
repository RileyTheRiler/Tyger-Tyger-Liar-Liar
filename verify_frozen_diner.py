import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("src"))

from game import Game

def verify_frozen_diner():
    print("=== Verifying Frozen Diner Scene ===")
    
    # Initialize Game
    game = Game()
    
    # Load Frozen Diner Scene
    print("\nLoading 'diner_frozen'...")
    scene = game.scene_manager.load_scene("diner_frozen")
    
    if not scene:
        print("FAIL: Could not load scene 'diner_frozen'")
        return
        
    print(f"PASS: Loaded scene '{scene['title']}'")
    
    # Verify Text Content (Unreliable Lens)
    print("\nVerifying Lens Text...")
    lens_text = scene.get('text', {}).get('lens', {})
    if 'believer' in lens_text and 'skeptic' in lens_text:
        print("PASS: Lens variants found")
    else:
        print("FAIL: Missing lens text")
        
    # Verify NPC Manager
    print("\nVerifying NPC Manager...")
    maude = game.npc_manager.get_npc("maude")
    if maude and maude['phase'] == 'wall':
        print(f"PASS: Maude loaded in correct initial phase '{maude['phase']}'")
    else:
        print(f"FAIL: Maude state incorrect (found {maude})")
        
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_frozen_diner()
