import sys
import os

sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('src/engine'))
sys.path.append(os.path.abspath('.'))

from game import Game
from population_system import PopulationEventType

def test_population_integration():
    game = Game()
    
    # Initial population should be 347
    assert game.population_system.population == 347
    
    # Record a death via game.modify_resonance
    game.modify_resonance(-8, "Massacre at the Diner")
    
    # Population should be 339 (347 - 8)
    assert game.population_system.population == 339
    
    # Check if threshold was triggered (340 is a threshold)
    triggered = game.population_system.get_triggered_thresholds()
    assert len(triggered) >= 1
    assert any(t.population == 340 for t in triggered)
    
    print("Population integration test passed!")

if __name__ == "__main__":
    test_population_integration()
