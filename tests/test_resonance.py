
import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

from tyger_game.engine.board_system import BoardSystem, BoardNode
from tyger_game.engine.character import Character
from tyger_game.engine.paradigm_system import ParadigmManager

def test_resonance_trigger():
    print("Testing Resonance Trigger...")
    board = BoardSystem()
    char = Character()
    
    # 1. Setup anomaly cluster
    a1 = BoardNode("anomaly_1", "Strange Radio Burst", "ANOMALY")
    a2 = BoardNode("anomaly_2", "Impossible Interference", "ANOMALY")
    board.add_node(a1)
    board.add_node(a2)
    
    # Connect them
    board.connect_nodes("anomaly_1", "anomaly_2", char)
    
    # 2. Check for resonance
    new_paradigms = board.check_for_resonance(char)
    print(f"  Detected resonances: {new_paradigms}")
    
    assert "signal_in_static" in new_paradigms
    print("  ✓ Resonance pattern detected correctly.")
    
    # 3. Test Paradigm Integration
    for p_id in new_paradigms:
        ParadigmManager.start_internalizing(char, p_id)
        
    assert any(p["id"] == "signal_in_static" for p in char.paradigms)
    print("  ✓ Paradigm internalization started.")

def test_glitch_flagging():
    print("\nTesting Glitch Flagging...")
    board = BoardSystem()
    char = Character()
    
    # Setup node
    anomaly = BoardNode("node_a", "Ghostly Figure", "ANOMALY", "SOFT")
    board.add_node(anomaly)
    
    # Moderate Skeptic
    char.active_alignment = "Debunker"
    char.alignment_scores["skeptic"] = 5
    
    data = board.get_redacted_node_data("node_a", char)
    assert data["is_glitched"] == True
    print("  ✓ Skeptic view correctly flags anomaly as glitched.")
    
    # Moderate Believer viewing Fact
    char.active_alignment = "Fundamentalist"
    char.alignment_scores["skeptic"] = 0
    char.alignment_scores["believer"] = 5
    fact = BoardNode("node_f", "Footprints", "FACT", "HARD")
    board.add_node(fact)
    
    data = board.get_redacted_node_data("node_f", char)
    assert data["is_glitched"] == True
    print("  ✓ Believer view correctly flags fact as glitched.")

if __name__ == "__main__":
    print("Verifying Psychological Resonance & Visual Glitches...")
    print("=" * 50)
    try:
        test_resonance_trigger()
        test_glitch_flagging()
        print("\n" + "=" * 50)
        print("Verification Successful! ✓")
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
