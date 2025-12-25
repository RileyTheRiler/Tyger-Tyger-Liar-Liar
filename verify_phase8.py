import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from text_composer import TextComposer
from fracture_manager import FractureManager

def verify_phase8():
    print("Verifying Phase 8: Unsafe Menu + Reality Fracture...")
    
    gs = GameState()
    # Trigger fracture condition: High attention
    gs.modify_attention(80) 
    
    composer = TextComposer(game_state=gs)
    fracture = FractureManager(gs, composer)
    
    print("\n--- Testing Menu Fracture (High Attention) ---")
    print("This has a 15% chance, so we'll try a few times until we see one or force it.")
    
    found = False
    for i in range(20):
        menu_text = fracture.get_menu_text("JOURNAL")
        if menu_text != "JOURNAL":
            print(f"Attempt {i+1}: FRACTURE DETECTED!")
            print(f"Result: {menu_text}")
            found = True
            break
            
    if not found:
        # Force a fracture by flag
        gs.apply_flag("trigger_fracture", True)
        menu_text = fracture.get_menu_text("JOURNAL")
        print(f"\nForced Fracture: {menu_text}")
        found = True

    if found:
        print("\n[SUCCESS] Unsafe menu / reality fracture verified.")
    else:
        print("\n[FAILURE] Reality fracture failed to trigger.")

if __name__ == "__main__":
    verify_phase8()
