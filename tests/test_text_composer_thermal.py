import sys
import os
import pytest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from text_composer import TextComposer, Archetype, ComposedText

@pytest.fixture
def composer():
    return TextComposer()

def test_thermal_mode_active_with_content(composer):
    """Test that thermal text overrides base text when mode is active."""
    data = {
        "base": "The room is dark.",
        "thermal": "The room glows with residual heat.",
        "lens": {"believer": "Ghosts are here."}
    }
    
    # Thermal OFF
    result_off = composer.compose(data, thermal_mode=False)
    assert "The room is dark." in result_off.full_text
    assert "residual heat" not in result_off.full_text
    
    # Thermal ON
    result_on = composer.compose(data, thermal_mode=True)
    assert "The room glows with residual heat." in result_on.full_text
    assert "The room is dark" not in result_on.full_text

def test_thermal_mode_fingertips_example(composer):
    """Test the specific example from the design doc."""
    data = {
        "base": "The Administrator shakes your hand. His grip is firm.",
        "thermal": "The Administrator shakes your hand. His palm is 101.4°F. The heat is localized in his fingertips."
    }
    
    result = composer.compose(data, thermal_mode=True)
    assert "101.4°F" in result.full_text
    assert "grip is firm" not in result.full_text

def test_thermal_fallback(composer):
    """If thermal mode is on but no thermal text provided, fallback to base."""
    data = {
        "base": "Just a normal room.",
        # No thermal key
    }
    
    result = composer.compose(data, thermal_mode=True)
    assert "Just a normal room." in result.full_text

def test_thermal_specific_inserts(composer):
    """Test inserts that only appear in thermal mode."""
    data = {
        "base": "Base text.",
        "thermal": "Thermal text.",
        "inserts": [
            {
                "id": "thermal_clue",
                "text": "You see a cold spot.",
                "condition": {"thermal_mode": True},
                "insert_at": "AFTER_BASE"
            },
            {
                "id": "normal_clue",
                "text": "You see a cup.",
                "condition": {"thermal_mode": False},
                "insert_at": "AFTER_BASE"
            }
        ]
    }
    
    # Thermal OFF
    result_off = composer.compose(data, thermal_mode=False)
    assert "You see a cup" in result_off.full_text
    assert "cold spot" not in result_off.full_text
    
    # Thermal ON
    result_on = composer.compose(data, thermal_mode=True)
    assert "Thermal text" in result_on.full_text
    assert "cold spot" in result_on.full_text
    assert "You see a cup" not in result_on.full_text
