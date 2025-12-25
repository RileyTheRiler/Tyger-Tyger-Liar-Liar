import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from board_manager import BoardManager

def verify_phase6():
    print("Verifying Phase 6: Board v1...")
    
    gs = GameState()
    board = BoardManager(gs)
    
    # 1. Add Clue with Auto-Link
    print("\n--- Testing Auto-Link ---")
    clue_data = {
        "title": "Strange Residue",
        "text": "A white powder that smells of ozone.",
        "links_to_theories": ["theory_ghost_machine"]
    }
    board.add_clue("clue_residue", clue_data)
    
    summary = board.get_board_summary()
    print(summary)
    
    if "clue_residue ---> theory_ghost_machine" in summary:
        print("[SUCCESS] Auto-linking verified.")
    else:
        print("[FAILURE] Auto-linking failed.")

    # 2. Start and Update Theory
    print("\n--- Testing Theory Internalization ---")
    theory_data = {
        "title": "Ghost in the Machine",
        "summary": "An entity residing in the local network.",
        "internalization_time": 60
    }
    board.start_theory("theory_ghost_machine", theory_data)
    
    print("State after starting theory:")
    print(board.get_board_summary())
    
    board.update_internalization(30)
    print("\nState after 30 minutes:")
    print(board.get_board_summary())
    
    board.update_internalization(30)
    print("\nState after another 30 minutes:")
    summary_final = board.get_board_summary()
    print(summary_final)
    
    if "theory_ghost_machine] [INTERNALIZED]" in summary_final:
        print("[SUCCESS] Theory internalization verified.")
    else:
        print("[FAILURE] Theory internalization failed.")

if __name__ == "__main__":
    verify_phase6()
