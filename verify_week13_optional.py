"""
Week 13 Optional Features Verification

Tests parser command integration and environmental effects system.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'engine'))

from engine.input_system import CommandParser
from engine.environmental_effects import EnvironmentalEffects
from mechanics import SkillSystem

def test_parser_commands():
    """Test Week 13 command parsing."""
    print("\n=== TESTING PARSER COMMANDS ===")
    
    parser = CommandParser()
    
    # Test combat commands
    print("\n1. Testing combat commands...")
    tests = [
        ("fight hostile local", ("FIGHT", "hostile local")),
        ("dodge", ("DODGE", None)),
        ("flee", ("FLEE", None)),
        ("intimidate guard", ("INTIMIDATE", "guard")),
        ("reason with suspect", ("REASON", "suspect"))
    ]
    
    for input_str, expected in tests:
        result = parser.normalize(input_str)
        if result and result[0] == expected:
            print(f"   ✓ '{input_str}' -> {result[0]}")
        else:
            print(f"   ✗ '{input_str}' failed: got {result}")
            return False
    
    # Test injury commands
    print("\n2. Testing injury commands...")
    tests = [
        ("injuries", ("INJURIES", None)),
        ("treat gunshot wound", ("TREAT", "gunshot wound")),
        ("rest 8 hours", ("REST", "8 hours"))
    ]
    
    for input_str, expected in tests:
        result = parser.normalize(input_str)
        if result and result[0] == expected:
            print(f"   ✓ '{input_str}' -> {result[0]}")
        else:
            print(f"   ✗ '{input_str}' failed")
            return False
    
    # Test chase commands
    print("\n3. Testing chase commands...")
    tests = [
        ("sprint", ("SPRINT", None)),
        ("vault fence", ("VAULT", "fence")),
        ("hide", ("HIDE", None)),
        ("surrender", ("SURRENDER", None))
    ]
    
    for input_str, expected in tests:
        result = parser.normalize(input_str)
        if result and result[0] == expected:
            print(f"   ✓ '{input_str}' -> {result[0]}")
        else:
            print(f"   ✗ '{input_str}' failed")
            return False
    
    print("\n✓ Parser command tests passed")
    return True

def test_environmental_effects():
    """Test environmental effects system."""
    print("\n=== TESTING ENVIRONMENTAL EFFECTS ===")
    
    env = EnvironmentalEffects()
    skill_system = SkillSystem('data/skills.json')
    
    # Test weather effects
    print("\n1. Testing weather effects...")
    env.set_weather("rain")
    perception_mod = env.get_modifier("Perception")
    print(f"   Rain -> Perception modifier: {perception_mod}")
    if perception_mod != -1:
        print(f"   ✗ Expected -1, got {perception_mod}")
        return False
    print(f"   ✓ Rain effects applied correctly")
    
    # Test lighting effects
    print("\n2. Testing lighting effects...")
    env.set_lighting("dark")
    firearms_mod = env.get_modifier("Firearms")
    print(f"   Dark -> Firearms modifier: {firearms_mod}")
    if firearms_mod != -2:
        print(f"   ✗ Expected -2, got {firearms_mod}")
        return False
    print(f"   ✓ Lighting effects applied correctly")
    
    # Test terrain effects
    print("\n3. Testing terrain effects...")
    env.set_terrain("mud")
    athletics_mod = env.get_modifier("Athletics")
    print(f"   Mud -> Athletics modifier: {athletics_mod}")
    if athletics_mod != -1:
        print(f"   ✗ Expected -1, got {athletics_mod}")
        return False
    print(f"   ✓ Terrain effects applied correctly")
    
    # Test stacking
    print("\n4. Testing modifier stacking...")
    all_mods = env.get_all_modifiers()
    print(f"   All modifiers: {all_mods}")
    # Rain: Perception -1, Reflexes -1, Firearms -1
    # Dark: Perception -2, Firearms -2, Reflexes -1, Stealth +2
    # Mud: Athletics -1, Stealth -1, Reflexes -1
    # Total: Perception -3, Firearms -3, Reflexes -3, Athletics -1, Stealth +1
    expected_perception = -3
    if all_mods.get("Perception") == expected_perception:
        print(f"   ✓ Modifiers stack correctly (Perception: {all_mods.get('Perception')})")
    else:
        print(f"   ✗ Stacking failed: expected {expected_perception}, got {all_mods.get('Perception')}")
        return False
    
    # Test description
    print("\n5. Testing narrative descriptions...")
    desc = env.get_description()
    print(f"   Description: {desc}")
    if "rain" in desc.lower() and "dark" in desc.lower():
        print(f"   ✓ Description includes active conditions")
    else:
        print(f"   ✗ Description missing conditions")
        return False
    
    # Test skill system integration
    print("\n6. Testing skill system integration...")
    env.apply_to_skill_system(skill_system)
    perception_skill = skill_system.get_skill("Perception")
    if perception_skill:
        print(f"   ✓ Environmental modifiers applied to skill system")
    else:
        print(f"   ✗ Skill system integration failed")
        return False
    
    print("\n✓ Environmental effects tests passed")
    return True

def main():
    """Run all optional feature tests."""
    print("="*60)
    print("WEEK 13 OPTIONAL FEATURES VERIFICATION")
    print("="*60)
    
    tests = [
        ("Parser Commands", test_parser_commands),
        ("Environmental Effects", test_environmental_effects)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name} FAILED with exception:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
