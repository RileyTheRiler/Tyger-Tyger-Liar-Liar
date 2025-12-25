
import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, 'src', 'engine'))

# Mock THEORY_DATA since board.py imports it
import types
theories_mock = types.ModuleType("theories")
theories_mock.THEORY_DATA = {
    "test_theory": {
        "name": "Test Theory",
        "category": "Paranormal",
        "description": "A test theory.",
        "lens_bias": "believer",
        "health": 40,
        "status": "active",
        "effects": {},
        "conflicts_with": [],
        "internalize_time_hours": 4,
        "active_case": False,
        "critical_for_endgame": False,
        "requirements": {},
        "unlocks": {},
        "on_internalize_effects": [],
        "degradation_rate": 10,
        "auto_locks": []
    }
}
sys.modules["theories"] = theories_mock

from src.engine.board import Board

def test_legacy_board_data():
    print("Testing Legacy Board Data Output...")
    board = Board()
    
    # 1. Test Glitch Logic (Skeptic viewing Believer theory with low health)
    data = board.get_board_data(archetype="skeptic", score_ratio=5)
    theory_node = next(n for n in data["nodes"] if n["id"] == "test_theory")
    
    assert theory_node["is_glitched"] == True
    assert "[LOGICAL ERROR]" in theory_node["label"]
    print("  ✓ Skeptic-induced glitching confirmed.")
    
    # 2. Test Friction Logic
    # Link some evidence
    theory = board.get_theory("test_theory")
    theory.linked_evidence.append("clue_1")
    
    data = board.get_board_data(archetype="skeptic", score_ratio=10)
    link = next(l for l in data["links"] if l["source"] == "clue_1")
    
    assert link["has_friction"] == True
    assert link["color"] == "#ff0000"
    print("  ✓ Epistemic Friction flagging confirmed.")

if __name__ == "__main__":
    print("Verifying Legacy Epistemic Friction Integration...")
    print("=" * 50)
    try:
        test_legacy_board_data()
        print("\n" + "=" * 50)
        print("Verification Successful! ✓")
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
