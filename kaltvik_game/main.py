import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game_loop import run_game_loop
from player.game_state import GameState

def start_game():
    """
    Initializes and starts the game.
    """
    print("====================================")
    print("       WELCOME TO KALTVIK           ")
    print("====================================")
    
    state = GameState()
    run_game_loop(state)

if __name__ == "__main__":
    start_game()
