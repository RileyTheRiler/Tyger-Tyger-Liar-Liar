"""
Week 13 Verification Script: Combat and Chase Systems

Tests all new Week 13 systems:
- Injury system (application, healing, treatment)
- Trauma system (Fortitude checks, narrative effects)
- Chase system (pursuit, obstacles, escape)
- Enhanced combat (dodge, talk, equipment integration)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ui'))

from engine.injury_system import InjurySystem
from engine.trauma_system import TraumaSystem
from engine.chase_system import ChaseSystem
from engine.combat import CombatManager
from mechanics import SkillSystem
from inventory_system import InventoryManager, Item

def test_injury_system():
    """Test injury application, healing, and treatment."""
    print("\\n=== TESTING INJURY SYSTEM ===")
    
    injury_system = InjurySystem()
    injury_system.load_injury_database('data/injuries.json')
    
    # Test injury application
    print("\\n1. Applying gunshot wound to leg...")
    injury = injury_system.apply_injury("gunshot_leg")
    print(f"   Applied: {injury.name}")
    print(f"   Effects: {injury.effects}")
    print(f"   Healing time: {injury.healing_time_hours}h")
    
    # Test penalty calculation
    print("\\n2. Checking skill penalties...")
    athletics_penalty = injury_system.get_penalty_for_skill("Athletics")
    print(f"   Athletics penalty: {athletics_penalty}")
    
    # Test healing progression
    print("\\n3. Advancing time (12 hours)...")
    messages = injury_system.advance_time(12.0)
    for msg in messages:
        print(f"   {msg}")
    
    # Test injury status
    print("\\n4. Injury status:")
    print(injury_system.get_injury_status())
    
    print("✓ Injury system tests passed")
    return True

def test_trauma_system():
    """Test trauma triggers, Fortitude checks, and narrative effects."""
    print("\\n=== TESTING TRAUMA SYSTEM ===")
    
    trauma_system = TraumaSystem()
    trauma_system.load_trauma_database('data/trauma_types.json')
    skill_system = SkillSystem('data/skills.json')
    player_state = {"sanity": 100.0, "reality": 100.0}
    
    # Test trauma trigger
    print("\\n1. Triggering trauma event (witness_death)...")
    result = trauma_system.check_trauma_trigger("witness_death", skill_system, player_state)
    print(f"   Trauma applied: {result['trauma_applied']}")
    print(f"   Message: {result['message']}")
    
    if result['trauma_applied']:
        trauma = result['trauma']
        print(f"   Trauma: {trauma.name}")
        print(f"   Effects: {trauma.effects}")
    
    # Test trauma triggers in scene
    print("\\n2. Checking trauma triggers...")
    triggered = trauma_system.check_trauma_triggers("You enter a dark room...")
    if triggered:
        for t in triggered:
            print(f"   Triggered: {t['effect']}")
    
    # Test trauma status
    print("\\n3. Trauma status:")
    print(trauma_system.get_trauma_status())
    
    # Test recovery
    print("\\n4. Advancing time (24 hours)...")
    messages = trauma_system.advance_time(24.0)
    for msg in messages:
        print(f"   {msg}")
    
    print("✓ Trauma system tests passed")
    return True

def test_chase_system():
    """Test chase sequences, obstacles, and escape mechanics."""
    print("\\n=== TESTING CHASE SYSTEM ===")
    
    chase_system = ChaseSystem()
    chase_system.load_chase_scenarios('data/chase_scenarios.json')
    skill_system = SkillSystem('data/skills.json')
    player_state = {"sanity": 100.0, "current_weather": "clear"}
    
    # Test chase start
    print("\\n1. Starting alley chase...")
    result = chase_system.start_chase("alley_pursuit", skill_system, player_state)
    print(f"   Started: {result['started']}")
    print(f"   Message: {result['message']}")
    print(f"   Available actions: {result['available_actions']}")
    
    # Test sprint action
    print("\\n2. Performing sprint action...")
    action_result = chase_system.perform_action("sprint", skill_system, player_state)
    for msg in action_result['messages']:
        print(f"   {msg}")
    
    # Test chase status
    print("\\n3. Chase status:")
    status = chase_system.get_chase_status()
    print(f"   Active: {status['active']}")
    print(f"   Round: {status['round']}")
    print(f"   Distance: {status['distance']}")
    
    print("✓ Chase system tests passed")
    return True

def test_combat_system():
    """Test enhanced combat with dodge, talk, and equipment integration."""
    print("\\n=== TESTING ENHANCED COMBAT SYSTEM ===")
    
    skill_system = SkillSystem('data/skills.json')
    player_state = {"sanity": 100.0, "injuries": []}
    injury_system = InjurySystem()
    injury_system.load_injury_database('data/injuries.json')
    inventory_system = InventoryManager()
    
    combat_manager = CombatManager(
        skill_system, 
        player_state,
        injury_system=injury_system,
        inventory_system=inventory_system
    )
    combat_manager.load_encounter_templates('data/encounters.json')
    
    # Test encounter start
    print("\\n1. Starting combat encounter...")
    combat_manager.start_encounter(encounter_id="hostile_local")
    print(f"   Active: {combat_manager.active}")
    print(f"   Enemies: {len(combat_manager.enemies)}")
    
    # Test dodge action
    print("\\n2. Performing dodge action...")
    result = combat_manager.perform_action("dodge")
    for msg in result['messages']:
        print(f"   {msg}")
    
    # Test attack action
    print("\\n3. Performing attack action...")
    result = combat_manager.perform_action("attack", target_name="Hostile Local")
    for msg in result['messages']:
        print(f"   {msg}")
    
    # Test combat log
    print("\\n4. Combat log:")
    for log_entry in combat_manager.log[-5:]:
        print(f"   {log_entry}")
    
    print("✓ Combat system tests passed")
    return True

def main():
    """Run all Week 13 verification tests."""
    print("="*60)
    print("WEEK 13 VERIFICATION: Combat and Chase Systems")
    print("="*60)
    
    tests = [
        ("Injury System", test_injury_system),
        ("Trauma System", test_trauma_system),
        ("Chase System", test_chase_system),
        ("Enhanced Combat", test_combat_system)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"\\n✗ {test_name} FAILED with exception:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
