
import sys
import os
import pytest
from unittest.mock import MagicMock

# Ensure src path is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from content.dialogue_manager import DialogueManager
from engine.mechanics import SkillSystem
from board import Board
from engine.psychological_system import PsychologicalState

# Mock PlayerState to behave like a dict but allow attribute access if needed by some systems
class MockPlayerState(dict):
    pass

@pytest.fixture
def dialogue_manager():
    skill_system = MagicMock(spec=SkillSystem)
    skill_system.check_passive_interrupts.return_value = []
    skill_system.get_skill.return_value = MagicMock(effective_level=10) # Pass all skill checks
    # Mock get_skill_total to return an integer
    skill_system.get_skill_total.return_value = 10
    # Mock interrupt_lines attribute
    skill_system.interrupt_lines = {}

    board = MagicMock(spec=Board)
    board.is_theory_active.return_value = True # Pass theory checks
    board.theories = {}

    player_state = MockPlayerState({
        "sanity": 100.0,
        "reality": 100.0,
        "hallucination_history": [],
        "turn_count": 0,
        "archetype": "Neutral",
        "mental_load": 0,
        "fear_level": 0,
        "disorientation": False,
        "instability": False
    })

    dm = DialogueManager(skill_system, board, player_state)

    # Load the test fixture
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures/dialogues')
    success = dm.load_dialogue("hallucination_demo", fixtures_dir)
    assert success, "Failed to load dialogue fixture"

    return dm

def test_high_sanity_view(dialogue_manager):
    """Verify a sane player sees reliable options and conditional options, but not hallucinations."""
    dm = dialogue_manager
    dm.player_state["sanity"] = 100.0

    data = dm.get_render_data()
    choices = [c['text'] for c in data['choices']]

    assert "Ask who they are." in choices
    assert "Wave politely." in choices
    assert "Deny their existence." in choices # Sanity > 50
    assert "Scream until your throat bleeds." not in choices # Reliability: false

def test_low_sanity_view(dialogue_manager):
    """Verify a low sanity player (Psychosis) sees hallucinations and misses valid options."""
    dm = dialogue_manager
    dm.player_state["sanity"] = 20.0 # Tier 1 (Psychosis)

    data = dm.get_render_data()
    choices = [c['text'] for c in data['choices']]

    # 1. Hallucination should be visible
    assert "Scream until your throat bleeds." in choices

    # 2. High sanity condition option should be hidden
    assert "Deny their existence." not in choices # Requires Sanity > 50

    # 3. One of the valid reliable options should be hidden (Hiding logic)
    # Valid reliable options are "Ask who they are." and "Wave politely."
    # The logic hides one randomly.
    valid_visible = [c for c in choices if c in ["Ask who they are.", "Wave politely."]]
    assert len(valid_visible) < 2, f"Should have hidden at least one valid option. Saw: {valid_visible}"

def test_hallucination_logging(dialogue_manager):
    """Verify that seeing a hallucinated option logs it."""
    dm = dialogue_manager
    dm.player_state["sanity"] = 10.0

    # Render to trigger the logging
    dm.get_render_data()

    history = dm.player_state["hallucination_history"]
    assert len(history) > 0
    # Check for partial match of the text
    assert any("false_choice_start_Scream un" in entry for entry in history)

def test_ambiguous_options_visibility(dialogue_manager):
    """Verify that ambiguous options respect visibility conditions if added."""
    dm = dialogue_manager

    node = dm.nodes["start"]
    # Add an ambiguous choice dynamically
    node["choices"].append({
        "text": "Ambiguous Option",
        "reliability": "ambiguous",
        "visibility_conditions": {"sanity_min": 90}
    })

    # Case 1: High Sanity -> Should see it
    dm.player_state["sanity"] = 95.0
    # Clear cache to force re-render
    dm._cached_choices = []

    data = dm.get_render_data()
    texts = [c['text'] for c in data['choices']]
    assert "Ambiguous Option" in texts

    # Case 2: Low Sanity -> Should NOT see it (condition failed)
    dm.player_state["sanity"] = 80.0
    # Clear cache
    dm._cached_choices = []

    data = dm.get_render_data()
    texts = [c['text'] for c in data['choices']]
    assert "Ambiguous Option" not in texts

if __name__ == "__main__":
    # Allow running directly
    sys.exit(pytest.main([__file__]))
