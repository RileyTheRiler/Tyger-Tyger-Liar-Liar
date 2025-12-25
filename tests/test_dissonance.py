
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.population_system import PopulationSystem
from engine.text_composer import TextComposer
from engine.skill_voice_manager import SkillVoiceManager

class TestDissonance(unittest.TestCase):
    def setUp(self):
        self.pop_system = PopulationSystem()
        self.composer = TextComposer()
        # Mock skill system for composer
        self.composer.skill_system = MagicMock()
        self.composer.skill_system.check_passive_interrupts.return_value = []
        
    def test_dissonance_calculation(self):
        """Verify get_dissonance_factor calculation."""
        # Baseline
        self.pop_system.population = 347
        self.assertEqual(self.pop_system.get_dissonance_factor(), 0.0)
        
        # Immediate small deviation (1 person)
        self.pop_system.population = 346
        self.pop_system.hours_off_target = 0
        factor = self.pop_system.get_dissonance_factor()
        # count_factor (0.1) * 0.3 + time_factor (0) * 0.7 = 0.03 -> Min clamped to 0.05
        self.assertEqual(factor, 0.05)
        
        # Saturation (24 hours off)
        self.pop_system.hours_off_target = 24
        # count_factor (0.1) * 0.3 + time_factor (1.0) * 0.7 = 0.03 + 0.7 = 0.73
        factor_sat = self.pop_system.get_dissonance_factor()
        self.assertAlmostEqual(factor_sat, 0.73, places=2)
        
        # Max deviation (>10 people, >24 hrs)
        self.pop_system.population = 330
        factor_max = self.pop_system.get_dissonance_factor()
        self.assertEqual(factor_max, 1.0)

    def test_text_glitches(self):
        """Verify _apply_dissonance_glitches modifies text."""
        # Low intensity - minimal change
        text = "The quick brown fox jumps."
        glitched_low = self.composer._apply_dissonance_glitches(text, 0.1)
        # Should be mostly same, maybe stutter
        
        # High intensity - definite change
        glitched_high = self.composer._apply_dissonance_glitches(text, 1.0)
        
        # Check for signature corruptions
        has_corruption = (
            "..." in glitched_high or 
            len(glitched_high.split()) > len(text.split()) or # Stutter added words
            "347" in glitched_high
        )
        self.assertTrue(has_corruption, f"Text failed to glitch at max intensity: {glitched_high}")

    def test_voice_manager_dissonance(self):
        """Verify SkillVoiceManager utilizes dissonance."""
        manager = SkillVoiceManager()
        
        # Force high dissonance
        # We need to monkeypatch random to ensure the dissonance branch triggers if chance based
        import random
        # Save state
        state = random.getstate()
        random.seed(42) # Deterministic
        
        # Trigger dissonance voice
        # Dissonance > 0.3 required for chance
        result = manager.get_interjection("REASON", "context", dissonance=1.0)
        
        # Restore
        random.setstate(state)
        
        self.assertIsNotNone(result)
        # Should use a dissonance template
        is_dissonant = any(t in result["text"] for t in manager.DISSONANCE_TEMPLATES) or "Statistical Anomaly" in result["text"]
        self.assertTrue(is_dissonant, f"Expected dissonance template, got: {result['text']}")

if __name__ == '__main__':
    unittest.main()
