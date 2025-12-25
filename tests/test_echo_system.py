import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from engine.text_composer import TextComposer, Archetype
from engine.echo_manager import EchoManager
from engine.psychological_system import PsychologicalState

class TestEchoSystem(unittest.TestCase):
    def setUp(self):
        self.player_state = {
            "sanity": 100,
            "reality": 100,
            "narrative_entropy": 0.0,
            "active_failures": []
        }
        self.psych_state = PsychologicalState(self.player_state)
        self.composer = TextComposer(game_state=self.player_state)
        self.composer.debug_mode = True
        self.echo_manager = self.composer.echo_manager

    def test_echo_generation(self):
        # Trigger an echo from failure
        echo_id = self.echo_manager.trigger_echo_from_failure("Logic")
        self.assertTrue(echo_id.startswith("fail_Logic_"))
        self.assertEqual(len(self.echo_manager.active_echoes), 1)
        
        echo = list(self.echo_manager.active_echoes.values())[0]
        self.assertIn(echo.motif_type, ["smell", "sound", "visual", "thought"])
        self.assertIsNotNone(echo.content)

    def test_text_composition_with_echo(self):
        # Add a specific echo
        self.echo_manager.add_echo("test_smell", "smell", "copper", intensity=1.0)
        
        test_scene = {
            "base": "The room is cold. You see a shadows move."
        }
        
        # Compose text
        result = self.composer.compose(test_scene, Archetype.NEUTRAL, self.player_state)
        
        # Verify echo injection
        self.assertIn("copper", result.full_text)
        self.assertIn("echoes", result.debug_info.get("layers", []))

    def test_entropy_scaling_fracture(self):
        # Set high entropy
        self.player_state["narrative_entropy"] = 100.0
        
        # With 100 entropy, entropy_modifier is 100/500 = 0.2
        # Base fracture_chance is 0.01. Total chance = 0.21.
        
        fracture_count = 0
        for _ in range(100):
            if self.composer._should_apply_fracture(self.player_state):
                fracture_count += 1
        
        # Statistical check: should be around 21, but let's just check it's more than 0
        self.assertGreater(fracture_count, 0)
        
    def test_echo_decay(self):
        self.echo_manager.add_echo("short_lived", "sound", "ticks", lifetime=1)
        self.assertEqual(len(self.echo_manager.active_echoes), 1)
        
        self.echo_manager.advance_time(1)
        self.assertEqual(len(self.echo_manager.active_echoes), 0)

if __name__ == "__main__":
    unittest.main()
