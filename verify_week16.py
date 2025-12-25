import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath('src'))
sys.path.append(os.path.abspath('src/engine'))

from attention_system import AttentionSystem
from population_system import PopulationSystem, PopulationEvent
from integration_system import IntegrationSystem
from npc_system import NPCSystem, NPC

def test_attention_system():
    print("\n=== TESTING ATTENTION SYSTEM ===")
    att = AttentionSystem()
    
    # Test non-taboo trigger
    print("Testing add_attention...")
    result = att.add_attention(10, "Testing")
    assert result["success"]
    assert att.attention_level == 10
    print(f"  Level: {att.attention_level} [OK]")
    
    # Test threshold effects
    print("Testing threshold effects...")
    att.attention_level = 30
    effects = att.get_threshold_effects()
    assert effects["signal_interference"]
    print("  Level 30 Effects [OK]")
    
    att.attention_level = 80
    effects = att.get_threshold_effects()
    assert effects["reality_drain_per_hour"] == 2
    print("  Level 80 Effects [OK]")
    
    # Test Integration Trigger
    att.attention_level = 100
    event = att.trigger_integration_attempt()
    assert event["triggered"]
    print("  Integration Trigger [OK]")

def test_population_system():
    print("\n=== TESTING POPULATION SYSTEM ===")
    pop = PopulationSystem()
    
    # Mock NPC System
    class MockNPCSystem:
        def __init__(self):
            self.npcs = {
                "npc1": NPC({"id": "npc1", "name": "TestNPC1", "initial_trust": 50}),
                "npc2": NPC({"id": "npc2", "name": "TestNPC2", "initial_trust": 50})
            }
        def get_npc(self, id): return self.npcs.get(id)
    
    npc_sys = MockNPCSystem()
    
    # Test 347 Rule Enforcement
    print("Testing 347 Rule Enforcement...")
    pop.population = 348
    pop.target_population = 347
    
    event = pop.enforce_347_rule(npc_sys)
    assert event is not None
    assert pop.population == 347
    assert not npc_sys.npcs["npc1"].flags.get("alive", True) or not npc_sys.npcs["npc2"].flags.get("alive", True)
    print(f"  Population corrected to {pop.population} [OK]")
    print(f"  Subtraction event: {event.description} [OK]")
    
    # Test Resonance
    print("Testing Resonance Violation...")
    pop.population = 346
    pop.hours_off_target = 25
    violation = pop.check_resonance_violation()
    assert violation["is_violation"]
    assert "entity_agitation" in [a["type"] for a in violation["actions"]]
    print("  Resonance Violation detected [OK]")

def test_integration_system():
    print("\n=== TESTING INTEGRATION SYSTEM ===")
    integ = IntegrationSystem()
    
    # Test NPC Integration
    print("Testing NPC Integration...")
    integ.integrate_npc("npc1", "Test")
    assert integ.is_npc_integrated("npc1")
    print("  NPC marked as integrated [OK]")
    
    # Test Thermal Signature
    print("Testing Thermal Signature...")
    thermal = integ.get_thermal_signature("npc1")
    assert thermal["is_anomalous"]
    print(f"  Thermal: {thermal['description']} [OK]")
    
    # Test Micro-pause
    print("Testing Micro-pause...")
    pause = integ.check_micro_pause("npc1", "where were you?")
    assert pause["pause_detected"]
    print("  Micro-pause detected [OK]")

if __name__ == "__main__":
    try:
        test_attention_system()
        test_population_system()
        test_integration_system()
        print("\nALL SYSTEMS VERIFIED SUCCESSFULLY")
    except AssertionError as e:
        print(f"\nVERIFICATION FAILED: {e}")
    except Exception as e:
        print(f"\nERROR: {e}")
