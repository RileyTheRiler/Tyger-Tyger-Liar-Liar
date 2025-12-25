#!/usr/bin/env python3
import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core_game import Game

if __name__ == "__main__":
    game = Game()
    start_id = sys.argv[1] if len(sys.argv) > 1 else "bedroom"
    game.run(start_id)
