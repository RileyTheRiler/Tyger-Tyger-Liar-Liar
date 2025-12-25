import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.engine.distortion_rules import DistortionManager

class TestDistortion(unittest.TestCase):
    def setUp(self):
        self.manager = DistortionManager()
        self.base_text = "The door is open. The light shines through the window. I see a tree outside."
        
    def test_determinism(self):
        """Test that same state produces same distortion."""
        state = {"sanity": 10, "reality": 10, "time": 100}
        
        result1 = self.manager.apply_distortions(self.base_text, state)
        result2 = self.manager.apply_distortions(self.base_text, state)
        
        print(f"\n[Determinism] Run 1: {result1}")
        print(f"[Determinism] Run 2: {result2}")
        
        self.assertEqual(result1, result2)
        
    def test_time_variation(self):
        """Test that different time produces different distortion."""
        state1 = {"sanity": 10, "reality": 10, "time": 100}
        state2 = {"sanity": 10, "reality": 10, "time": 101}
        
        result1 = self.manager.apply_distortions(self.base_text, state1)
        result2 = self.manager.apply_distortions(self.base_text, state2)
        
        print(f"\n[Variation] Time 100: {result1}")
        print(f"[Variation] Time 101: {result2}")
        
        self.assertNotEqual(result1, result2)

    def test_intensity_scaling(self):
        """Test that low stress = no distortion, high stress = distortion."""
        safe_state = {"sanity": 100, "reality": 100}
        danger_state = {"sanity": 10, "reality": 10}
        
        safe_result = self.manager.apply_distortions(self.base_text, safe_state)
        danger_result = self.manager.apply_distortions(self.base_text, danger_state)
        
        print(f"\n[Scaling] Safe: {safe_result}")
        print(f"[Scaling] Danger: {danger_result}")
        
        self.assertEqual(safe_result, self.base_text)
        self.assertNotEqual(danger_result, self.base_text)
        
    def test_substitution(self):
        """Test specific word substitutions."""
        text = "Open the door and look at the reflection."
        state = {"sanity": 0, "reality": 0, "time": 12345} # Max intensity
        
        found_change = False
        for offset in range(10):
            state = {"sanity": 0, "reality": 0, "time": 12345 + offset}
            result = self.manager.apply_distortions(text, state)
            print(f"[Substitution Try {offset}] Out: {result}")
            if result != text:
                found_change = True
                break
        
        self.assertTrue(found_change, "Text should distort with max stress")

if __name__ == '__main__':
    unittest.main()
