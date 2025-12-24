import os
import sys

# Add project root to path so we can run from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tyger_game.engine.scene_manager import SceneManager
from tyger_game.engine.parser import CommandParser
from tyger_game.engine.character import Character
from tyger_game.ui.interface import print_header, print_text, get_input, clear_screen, Colors

def main():
    clear_screen()
    print_header("TYGER TYGER LIAR LIAR - PROTOTYPE")
    
    # Initialize Engine
    base_path = os.path.dirname(os.path.abspath(__file__))
    scene_manager = SceneManager(base_path) # Data is in tyger_game/data/scenes... wait path resolution might be tricky
    # Adjust path: tyger_game/main.py -> tyger_game/data
    scene_manager.data_path = os.path.join(base_path, "data")
    
    player = Character()
    parser = CommandParser(scene_manager, player)

    # Load Initial Scene
    try:
        scene_manager.load_scene("intro")
    except Exception as e:
        print_text(f"CRITICAL ERROR: Could not load intro scene. {e}", Colors.FAIL)
        return

    # Initial Description
    parser._handle_look_scene()

    # Game Loop
    running = True
    while running:
        try:
            player_input = get_input("\n> ")
            result = parser.parse(player_input)
            
            if result == "quit":
                running = False
                print_text("Goodbye.", Colors.HEADER)
        
        except KeyboardInterrupt:
            running = False
            print_text("\n\nGame Terminated.", Colors.FAIL)

if __name__ == "__main__":
    main()
