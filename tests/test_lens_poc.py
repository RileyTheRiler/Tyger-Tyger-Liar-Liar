
import json
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from engine.lens_system import LensSystem
from engine.text_composer import TextComposer, Archetype, ComposedText
from engine.game_state import GameState

# Mock Skill System for testing
class MockSkillSystem:
    def __init__(self, skills=None):
        self.skills = skills or {}

    def get_skill_total(self, skill_name):
        return self.skills.get(skill_name, 0)

    def get_skill(self, skill_name):
        class Skill:
            def __init__(self, val):
                self.effective_level = val
        return Skill(self.skills.get(skill_name, 0))

    def check_theory_commentary(self, active_theories):
        return []

# Mock Board
class MockBoard:
    def __init__(self):
        self.theories = {}

# Test Logic
def run_test():
    print("=== LENS SYSTEM PROOF OF CONCEPT TEST ===")

    # 1. Load the scene
    scene_path = "data/scenes/proof_of_concept.json"
    if not os.path.exists(scene_path):
        print(f"Error: Scene file not found at {scene_path}")
        return

    with open(scene_path, "r") as f:
        scene_data = json.load(f)

    print(f"Loaded Scene: {scene_data['name']}")

    # 2. Setup mock systems
    skill_system = MockSkillSystem({"Paranormal Sensitivity": 0, "Logic": 0})
    board = MockBoard()

    # 3. Test Cases: Archetypes + Stress
    test_cases = [
        ("Neutral / Low Stress", "neutral", 100, {}),
        ("Believer / Low Stress", "believer", 100, {}),
        ("Skeptic / Low Stress", "skeptic", 100, {}),
        ("Haunted / High Stress (Sanity 30)", "haunted", 30, {}),
    ]

    for label, archetype_str, sanity, skills in test_cases:
        print(f"\n--- TEST: {label} ---")

        # Configure GameState
        game_state = GameState()
        game_state.sanity = sanity
        game_state.archetype = archetype_str

        # Configure Lens System
        lens_system = LensSystem(skill_system, board, game_state)

        # Configure Text Composer
        composer = TextComposer(skill_system, board, game_state, lens_system)

        # Determine archetype enum (simulating what the game loop would do)
        # Note: In the real game, TextComposer calls calculate_dominant_lens which calls LensSystem.calculate_lens

        # Use the lens system to calculate (which should respect the logic we added)
        detected_lens_str = lens_system.calculate_lens()
        print(f"Detected Lens String: {detected_lens_str}")

        try:
             archetype = Archetype(detected_lens_str)
        except ValueError:
             print(f"Warning: Could not convert '{detected_lens_str}' to Archetype Enum. Defaulting to NEUTRAL.")
             archetype = Archetype.NEUTRAL

        # If we are testing specific archetypes that depend on skills (which are 0 here),
        # the calculate_lens might return Neutral unless we force it or set skills.
        # But for the HAUNTED case (Sanity < 40), it should auto-detect.
        # For Believer/Skeptic, we need to manually override for this test unless we mock skills.

        if archetype_str != "neutral" and archetype_str != "haunted":
             # Force it for the test output demonstration
             archetype = Archetype(archetype_str)
             print(f"Forcing Archetype to: {archetype}")

        # Compose
        result = composer.compose(scene_data, archetype, game_state.to_dict())

        print(f"RESOLVED TEXT ({archetype.value}):")
        print(result.full_text[:200] + "...") # Print start of text
        print("-" * 20)

        # Verification
        if archetype_str == "believer":
            assert "whispering" in result.full_text or "spirit" in result.full_text or "cold spot" in result.full_text, "Believer text missing"
        elif archetype_str == "skeptic":
            assert "interference" in result.full_text or "wiring" in result.full_text, "Skeptic text missing"
        elif archetype_str == "haunted":
            assert "scream" in result.full_text or "remember" in result.full_text, "Haunted text missing"
        elif archetype_str == "neutral":
             assert "static fills" in result.full_text, "Neutral text missing"

    print("\n=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    run_test()
