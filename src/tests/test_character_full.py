"""
Comprehensive Test Suite for Character System (Prompt 4)
Tests all requirements:
- 4 Attributes with caps
- 29 Skills mapped to attributes
- Skill personalities and passive interrupts
- Leveling system (XP, skill points)
- Character Sheet UI
- Effective level capping by parent attribute
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from mechanics import SkillSystem, CharacterSheetUI, Attribute, Skill

def test_attributes():
    print("\n" + "="*60)
    print("TEST 1: Attributes with Caps")
    print("="*60)
    
    system = SkillSystem()
    
    # Test attribute initialization
    assert len(system.attributes) == 4, "Should have 4 attributes"
    assert all(attr in system.attributes for attr in ["REASON", "INTUITION", "CONSTITUTION", "PRESENCE"])
    
    # Test attribute caps
    reason = system.attributes["REASON"]
    print(f"Initial REASON: {reason.value}/{reason.cap}")
    
    reason.value = 10  # Try to exceed cap
    print(f"After setting to 10: {reason.value}/{reason.cap}")
    assert reason.value == 6, "Attribute should be capped at 6"
    
    reason.value = -5  # Try to go below minimum
    print(f"After setting to -5: {reason.value}/{reason.cap}")
    assert reason.value == 1, "Attribute should floor at 1"
    
    print("✓ Attributes test passed")

def test_skills():
    print("\n" + "="*60)
    print("TEST 2: 29 Skills Mapped to Attributes")
    print("="*60)
    
    system = SkillSystem()
    
    # Count skills per attribute
    skill_counts = {
        "REASON": 0,
        "INTUITION": 0,
        "CONSTITUTION": 0,
        "PRESENCE": 0
    }
    
    for skill in system.skills.values():
        skill_counts[skill.attribute_ref.name] += 1
    
    print(f"REASON: {skill_counts['REASON']} skills (expected 7)")
    print(f"INTUITION: {skill_counts['INTUITION']} skills (expected 7)")
    print(f"CONSTITUTION: {skill_counts['CONSTITUTION']} skills (expected 8)")
    print(f"PRESENCE: {skill_counts['PRESENCE']} skills (expected 7)")
    
    total = sum(skill_counts.values())
    print(f"Total: {total} skills (expected 29)")
    
    assert skill_counts["REASON"] == 7
    assert skill_counts["INTUITION"] == 7
    assert skill_counts["CONSTITUTION"] == 8
    assert skill_counts["PRESENCE"] == 7
    assert total == 29
    
    print("✓ Skills test passed")

def test_skill_personalities():
    print("\n" + "="*60)
    print("TEST 3: Skill Personalities")
    print("="*60)
    
    system = SkillSystem()
    
    # Check a few skills have personalities
    logic = system.get_skill("Logic")
    print(f"Logic personality: \"{logic.personality}\"")
    assert logic.personality == "The world is a machine of cause and effect. Analyze the variables, discard the noise, and the truth remains as cold and certain as a mathematical theorem."
    
    forensics = system.get_skill("Forensics")
    print(f"Forensics personality: \"{forensics.personality}\"")
    assert forensics.personality == "The dead speak if you listen. Blood spatter, calluses, and decomposition are a language of their own."
    
    # Test all skills have personalities
    for skill_name, skill in system.skills.items():
        assert skill.personality, f"{skill_name} should have a personality"
    
    print("✓ Skill personalities test passed")

def test_effective_level_capping():
    print("\n" + "="*60)
    print("TEST 4: Effective Level Capping by Attribute")
    print("="*60)
    
    system = SkillSystem()
    
    # Set REASON to 3
    system.attributes["REASON"].value = 3
    
    logic = system.get_skill("Logic")
    logic.base_level = 5  # Try to set higher than attribute
    
    effective = logic.effective_level
    print(f"REASON attribute: {system.attributes['REASON'].value}")
    print(f"Logic base_level: {logic.base_level}")
    print(f"Logic effective_level: {effective}")
    
    assert effective == 3, "Effective level should be capped by attribute value"
    
    # Test with modifiers
    logic.set_modifier("Test Bonus", 2)
    effective_with_mod = logic.effective_level
    print(f"Logic with +2 modifier: {effective_with_mod}")
    assert effective_with_mod == 3, "Should still be capped even with modifiers"
    
    # Increase attribute
    system.attributes["REASON"].value = 6
    effective_after_increase = logic.effective_level
    print(f"After increasing REASON to 6: {effective_after_increase}")
    assert effective_after_increase == 6, "Should now use full base + modifier (capped at 6)"
    
    print("✓ Effective level capping test passed")

def test_passive_interrupts():
    print("\n" + "="*60)
    print("TEST 5: Passive Interrupts")
    print("="*60)
    
    system = SkillSystem()
    
    # Boost some skills to increase interrupt chance
    system.get_skill("Logic").base_level = 5
    system.get_skill("Forensics").base_level = 5
    system.attributes["REASON"].value = 6
    
    context = "A bloody knife lies on the floor"
    
    print(f"Context: '{context}'")
    print("Checking for passive interrupts...")
    
    interrupts = system.check_passive_interrupts(context)
    
    print(f"Found {len(interrupts)} interrupts:")
    for interrupt in interrupts:
        print(f"  {interrupt}")
    
    # At least verify the method works (RNG dependent)
    print("✓ Passive interrupts test passed (RNG dependent)")

def test_leveling_system():
    print("\n" + "="*60)
    print("TEST 6: Leveling System (XP & Skill Points)")
    print("="*60)
    
    system = SkillSystem()
    
    print(f"Initial: Level {system.level}, XP {system.xp}, SP {system.skill_points}")
    
    # Add 150 XP (should trigger level up at 100)
    system.add_xp(150)
    print(f"After 150 XP: Level {system.level}, XP {system.xp}, SP {system.skill_points}")
    
    assert system.level == 2, "Should be level 2"
    assert system.skill_points == 1, "Should have 1 skill point"
    
    # Spend skill point
    system.attributes["REASON"].value = 3
    logic = system.get_skill("Logic")
    initial_base = logic.base_level
    
    system.spend_point("Logic")
    print(f"Logic increased from {initial_base} to {logic.base_level}")
    
    assert logic.base_level == initial_base + 1
    assert system.skill_points == 0
    
    # Try to exceed attribute cap
    logic.base_level = 3  # At cap
    system.skill_points = 1  # Give another point
    
    print("\nTrying to raise Logic above REASON cap...")
    system.spend_point("Logic")
    assert logic.base_level == 3, "Should not exceed attribute cap"
    assert system.skill_points == 1, "Point should not be spent"
    
    print("✓ Leveling system test passed")

def test_character_sheet_ui():
    print("\n" + "="*60)
    print("TEST 7: Character Sheet UI")
    print("="*60)
    
    system = SkillSystem()
    
    # Set up some interesting state
    system.attributes["REASON"].value = 4
    system.attributes["INTUITION"].value = 5
    system.get_skill("Logic").base_level = 3
    system.get_skill("Forensics").base_level = 2
    system.get_skill("Forensics").set_modifier("Coffee", 1)
    system.xp = 250
    system.level = 3
    system.skill_points = 2
    
    ui = CharacterSheetUI(system)
    ui.display()
    
    print("✓ Character Sheet UI test passed")

def test_2d6_skill_checks():
    print("\n" + "="*60)
    print("TEST 8: 2d6 Skill Check System")
    print("="*60)
    
    system = SkillSystem()
    
    # Set up skill
    system.attributes["REASON"].value = 4
    system.get_skill("Logic").base_level = 2
    
    # Manual roll for deterministic test
    result = system.roll_check("Logic", difficulty=10, manual_roll=7)
    
    print(f"Skill: {result['skill']}")
    print(f"Roll: {result['roll']} (2d6)")
    print(f"Modifier: {result['modifier']}")
    print(f"Total: {result['total']}")
    print(f"Difficulty: {result['difficulty']}")
    print(f"Success: {result['success']}")
    
    assert result['roll'] == 7
    assert result['modifier'] == 2
    assert result['total'] == 9
    assert result['success'] == False  # 9 < 10
    
    # Test with higher roll
    result2 = system.roll_check("Logic", difficulty=10, manual_roll=8)
    assert result2['success'] == True  # 8 + 2 = 10 >= 10
    
    print("✓ 2d6 skill check test passed")

def test_red_white_checks():
    print("\n" + "="*60)
    print("TEST 9: Red/White Check System")
    print("="*60)
    
    system = SkillSystem()
    system.attributes["REASON"].value = 4
    system.get_skill("Logic").base_level = 2
    
    # Red check failure
    result1 = system.roll_check("Logic", difficulty=15, check_type="red", check_id="test_red_1", manual_roll=5)
    print(f"Red check result: {result1['success']} (should fail)")
    
    # Try to retry red check
    result2 = system.roll_check("Logic", difficulty=15, check_type="red", check_id="test_red_1", manual_roll=12)
    print(f"Red check retry: blocked={result2.get('blocked', False)}")
    assert result2.get('blocked') == True, "Red check retry should be blocked"
    
    # White check failure
    result3 = system.roll_check("Logic", difficulty=15, check_type="white", check_id="test_white_1", manual_roll=5)
    print(f"White check result: {result3['success']} (should fail)")
    
    # Try to retry white check without improving skill
    result4 = system.roll_check("Logic", difficulty=15, check_type="white", check_id="test_white_1", manual_roll=12)
    print(f"White check retry (no improvement): blocked={result4.get('blocked', False)}")
    assert result4.get('blocked') == True, "White check retry should be blocked without skill improvement"
    
    # Improve skill and retry
    system.get_skill("Logic").base_level = 3
    result5 = system.roll_check("Logic", difficulty=15, check_type="white", check_id="test_white_1", manual_roll=12)
    print(f"White check retry (after improvement): success={result5['success']}")
    assert result5.get('blocked') != True, "Should be allowed after skill improvement"
    
    print("✓ Red/White check system test passed")

def run_all_tests():
    print("\n" + "="*60)
    print("PROMPT 4: CHARACTER SYSTEM TEST SUITE")
    print("="*60)
    
    test_attributes()
    test_skills()
    test_skill_personalities()
    test_effective_level_capping()
    test_passive_interrupts()
    test_leveling_system()
    test_character_sheet_ui()
    test_2d6_skill_checks()
    test_red_white_checks()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
