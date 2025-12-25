import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))
sys.path.append(str(src_dir / "ui"))
sys.path.append(str(src_dir / "content"))

# Import Game
try:
    from game import Game
    from text_composer import TextComposer
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Mock print to capture output
captured_output = []
def mock_print(text):
    captured_output.append(str(text))

def verify_full_stack():
    print("=== VERIFYING FULL STACK (USER CHANGES) ===\n")
    
    print("1. Initializing Game Engine...")
    try:
        game = Game()
        # Monkeypatch print
        game.print = mock_print
    except Exception as e:
        print(f"[FATAL] Could not initialize Game: {e}")
        import traceback
        traceback.print_exc()
        return

    print("   [OK] Game initialized.")

    # --- TEST 1: EXAMINE COMMAND ---
    print("\n2. Testing EXAMINE Command (Fuzzy Match & Thermal)...")
    
    # Inject test scene data
    game.scene_manager.current_scene_data = {
        "id": "test_scene",
        "objects": {
            "shiny_box": {
                "description": "It is a very shiny metal box.", 
                "temperature": 105.0
            }
        }
    }
    
    # Test valid fuzzy match
    captured_output.clear()
    game.handle_parser_command("EXAMINE", "box")
    output_str = "\n".join(captured_output)
    
    if "very shiny" in output_str:
        print("   [PASS] Fuzzy match 'box' -> 'shiny_box'")
    else:
        print(f"   [FAIL] Fuzzy match failed. Output:\n{output_str}")

    # Test Thermal Mode
    game.player_state["thermal_mode"] = True
    captured_output.clear()
    game.handle_parser_command("EXAMINE", "box")
    output_str = "\n".join(captured_output)
    
    if "THERMAL READING: 105.0" in output_str:
        print("   [PASS] Thermal reading displayed")
    else:
        print(f"   [FAIL] Thermal reading missing. Output:\n{output_str}")

    # --- TEST 2: TEXT COMPOSER THEORY COMMENTARY ---
    print("\n3. Testing TextComposer Theory Commentary...")
    
    # Find or create text composer
    composer = None
    if hasattr(game, "liar_engine"):
        if hasattr(game.liar_engine, "composer"):
            composer = game.liar_engine.composer
    
    if not composer:
        # Fallback: Create new
        print("   (Creating standalone TextComposer for test)")
        composer = TextComposer(skill_system=game.skill_system, board=game.board, game_state=game.player_state)
    
    # Inject Mock Commentary Logic into SkillSystem
    # We monkeypatch the method on the instance
    def mock_check_commentary(active_theories):
        return [{"skill": "Logic", "text": "This is a verified theory intrusion."}]
    
    game.skill_system.check_theory_commentary = mock_check_commentary
    
    # Set active theory in state
    game.player_state["active_theories"] = ["theory_test"]
    
    # Compose
    result = composer.compose({"base": "The room is quiet."}, player_state=game.player_state)
    
    if "[Logic]: *This is a verified theory intrusion.*" in result.full_text:
        print("   [PASS] Theory commentary injected into text.")
    else:
        print(f"   [FAIL] Commentary missing. Full text:\n{result.full_text}")
        print(f"   Debug Info: {result.debug_info}")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    verify_full_stack()
