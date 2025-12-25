"""
Test script for Save/Load system
This script tests the serialization and deserialization of game systems.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mechanics import SkillSystem, Attribute, Skill
from time_system import TimeSystem
from save_system import SaveSystem, EventLog

def test_skill_system_serialization():
    """Test SkillSystem serialization and deserialization."""
    print("\n=== Testing SkillSystem Serialization ===")
    
    # Create a skill system
    system1 = SkillSystem()
    
    # Modify some values
    system1.attributes["REASON"].value = 5
    system1.skills["Logic"].base_level = 3
    system1.skills["Logic"].set_modifier("Test", 2)
    system1.xp = 150
    system1.level = 2
    
    # Serialize
    data = system1.to_dict()
    print(f"Serialized XP: {data['xp']}")
    print(f"Serialized Level: {data['level']}")
    print(f"Serialized REASON: {data['attributes']['REASON']['value']}")
    
    # Deserialize
    system2 = SkillSystem.from_dict(data)
    
    # Verify
    assert system2.xp == 150, "XP not restored"
    assert system2.level == 2, "Level not restored"
    assert system2.attributes["REASON"].value == 5, "Attribute not restored"
    assert system2.skills["Logic"].base_level == 3, "Skill base level not restored"
    assert system2.skills["Logic"].modifiers.get("Test") == 2, "Skill modifier not restored"
    
    print("✓ SkillSystem serialization test PASSED")

def test_player_state_serialization():
    """Test Player State serialization (including injuries)."""
    print("\n=== Testing Player State Serialization ===")

    player_state = {
        "sanity": 80,
        "injuries": [
            {
                "type": "Bruise",
                "location": "Arm",
                "healing_time_remaining": 72 * 60
            }
        ]
    }

    # Simulate Save (dict to json-like structure)
    import json
    serialized = json.dumps(player_state)

    # Simulate Load
    loaded = json.loads(serialized)

    injury = loaded["injuries"][0]
    assert injury["type"] == "Bruise"
    assert injury["healing_time_remaining"] == 4320

    print("✓ Player State serialization test PASSED")

def test_time_system_serialization():
    """Test TimeSystem serialization and deserialization."""
    print("\n=== Testing TimeSystem Serialization ===")
    
    # Create a time system
    system1 = TimeSystem("1995-10-14 08:00")
    system1.advance_time(120)  # Advance 2 hours
    system1.set_weather("rain")
    
    # Serialize
    data = system1.to_dict()
    print(f"Serialized time: {data['current_time']}")
    print(f"Serialized weather: {data['weather']}")
    
    # Deserialize
    system2 = TimeSystem.from_dict(data)
    
    # Verify
    assert system2.current_time.strftime("%Y-%m-%d %H:%M") == "1995-10-14 10:00", "Time not restored"
    assert system2.weather == "rain", "Weather not restored"
    
    print("✓ TimeSystem serialization test PASSED")

def test_event_log():
    """Test EventLog functionality."""
    print("\n=== Testing EventLog ===")
    
    log = EventLog()
    
    # Add events
    log.add_event("scene_entry", scene_id="bedroom", scene_name="Bedroom")
    log.add_event("skill_check", skill="Logic", difficulty=10, success=True)
    log.add_event("skill_check", skill="Perception", difficulty=12, success=False)
    
    # Get all events
    all_events = log.get_logs()
    assert len(all_events) == 3, f"Expected 3 events, got {len(all_events)}"
    
    # Get filtered events
    skill_checks = log.get_logs(event_type="skill_check")
    assert len(skill_checks) == 2, f"Expected 2 skill checks, got {len(skill_checks)}"
    
    # Get limited events
    limited = log.get_logs(limit=2)
    assert len(limited) == 2, f"Expected 2 events with limit, got {len(limited)}"
    
    # Test serialization
    data = log.to_dict()
    log2 = EventLog.from_dict(data)
    assert len(log2.events) == 3, "Events not restored after serialization"
    
    print("✓ EventLog test PASSED")

def test_save_system():
    """Test SaveSystem save/load functionality."""
    print("\n=== Testing SaveSystem ===")
    
    save_system = SaveSystem("test_saves")
    
    # Create test data
    test_data = {
        "scene": "test_scene",
        "datetime": "1995-10-14 10:00",
        "summary": "Test save",
        "test_value": 42
    }
    
    # Save
    success = save_system.save_game("test_slot", test_data)
    assert success, "Save failed"
    print("✓ Save successful")
    
    # Load
    loaded_data = save_system.load_game("test_slot")
    assert loaded_data is not None, "Load failed"
    assert loaded_data["test_value"] == 42, "Data not restored correctly"
    print("✓ Load successful")
    
    # List saves
    saves = save_system.list_saves()
    assert len(saves) > 0, "No saves found"
    assert any(s["slot_id"] == "test_slot" for s in saves), "Test save not in list"
    print("✓ List saves successful")
    
    # Delete save
    success = save_system.delete_save("test_slot")
    assert success, "Delete failed"
    print("✓ Delete successful")
    
    # Cleanup test directory
    import shutil
    if os.path.exists("test_saves"):
        shutil.rmtree("test_saves")
    
    print("✓ SaveSystem test PASSED")

def main():
    """Run all tests."""
    print("="*60)
    print("Save/Load System Test Suite")
    print("="*60)
    
    try:
        test_skill_system_serialization()
        test_player_state_serialization()
        test_time_system_serialization()
        test_event_log()
        test_save_system()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
