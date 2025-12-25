import sys
import os
# Ensure project root and src/tyger_game are in path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

from tyger_game.engine.board_system import BoardSystem, BoardNode
from tyger_game.engine.character import Character
from src.engine.text_composer import TextComposer, Archetype
from src.engine.distortion_rules import DistortionManager
from src.engine.parser_hallucination import ParserHallucinationEngine

def test_board_redaction():
    print("Testing Board Redaction...")
    board = BoardSystem()
    char = Character()
    
    # Setup nodes
    anomaly = BoardNode("node_a", "Ghostly Figure", "ANOMALY", "SOFT")
    fact = BoardNode("node_f", "Footprints", "FACT", "HARD")
    board.add_node(anomaly)
    board.add_node(fact)
    
    # Test Skeptic redaction
    char.active_alignment = "Debunker"
    char.alignment_scores["skeptic"] = 5
    char.alignment_scores["believer"] = 0
    
    data = board.get_redacted_node_data("node_a", char)
    assert "[LOGICAL ERROR" in data["description"]
    print("  ✓ Skeptic redaction of Anomaly working.")
    
    # Test Believer redaction
    char.active_alignment = "Fundamentalist"
    char.alignment_scores["skeptic"] = 0
    char.alignment_scores["believer"] = 5
    
    data = board.get_redacted_node_data("node_f", char)
    assert "[IRRELEVANT NOISE" in data["description"]
    print("  ✓ Believer redaction of Fact working.")

def test_archetype_distortion():
    print("\nTesting Archetype Distortion...")
    dm = DistortionManager()
    
    # High stress state
    state = {
        "sanity": 20,
        "reality": 20,
        "fear_level": 80,
        "time": 100
    }
    
    text = "The truth is hidden in the system data."
    
    # Skeptic distortions
    skeptic_dist = dm.apply_distortions(text, state, "skeptic")
    print(f"  Skeptic output: {skeptic_dist}")
    # Check if a skeptic replacement occurred (probabilistic, so we might need a fixed seed or multiple runs)
    # But since it's a test, we expect SOMETHING to change if intensity is 1.0
    
    # Believer distortions
    believer_dist = dm.apply_distortions(text, state, "believer")
    print(f"  Believer output: {believer_dist}")
    
    assert skeptic_dist != text or believer_dist != text
    print("  ✓ Distortion applied.")

def test_hallucination_verbs():
    print("\nTesting Hallucination Verbs...")
    phe = ParserHallucinationEngine()
    
    skeptic_verbs = phe.generate_ghost_commands(10, "skeptic")
    assert "DEBUG" in skeptic_verbs or "VERIFY" in skeptic_verbs
    print(f"  ✓ Skeptic ghost verbs present: {skeptic_verbs}")
    
    believer_verbs = phe.generate_ghost_commands(10, "believer")
    assert "ASCEND" in believer_verbs or "BEHOLD" in believer_verbs
    print(f"  ✓ Believer ghost verbs present: {believer_verbs}")

if __name__ == "__main__":
    print("Verifying Lens-Aware Redaction & Distortion...")
    print("=" * 50)
    try:
        test_board_redaction()
        test_archetype_distortion()
        test_hallucination_verbs()
        print("\n" + "=" * 50)
        print("Verification Successful! ✓")
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
