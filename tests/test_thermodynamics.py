import sys
import os
import pytest

sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('.'))

from game import Game
from mechanics import SkillSystem

class MockOutput:
    def __init__(self):
        self.buffer = []
    def print(self, text):
        self.buffer.append(text)
    def flush(self):
        return "\n".join(self.buffer)
    def clear(self):
        self.buffer = []

def test_thermodynamics_check():
    game = Game()
    game.output = MockOutput() # Mock output to capture prints
    
    # 1. Setup Scene with HOT object
    scene_data = {
        "text": "A room.",
        "objects": {
            "Furnace": {"description": "Burny.", "temperature": 150.0},
            "Ice": {"description": "Cold.", "temperature": 10.0}
        }
    }
    
    # Force high skills to ensure checks pass
    game.skill_system.skills["Medicine"].base_level = 10
    game.skill_system.skills["Logic"].base_level = 10
    
    # 2. Run Check - Expectations: Both trigger
    game.check_thermal_signatures(scene_data)
    
    output = game.output.flush()
    print("Output:", output)
    
    assert "[MEDICINE]" in output
    assert "Furnace" in output
    assert "150.0" in output
    
    assert "[LOGIC]" in output
    assert "Ice" in output
    assert "10.0" in output

def test_thermodynamics_neutral():
    game = Game()
    game.output = MockOutput()
    
    scene_data = {
        "text": "A room.",
        "objects": {
            "Chair": {"description": "Sit.", "temperature": 70.0}
        }
    }
    game.check_thermal_signatures(scene_data)
    output = game.output.flush()
    assert output == "" # No triggers for neutral temp

if __name__ == "__main__":
    test_thermodynamics_check()
    test_thermodynamics_neutral()
    print("Thermodynamic tests passed.")
