from character_system import Character, CharacterSheetUI

def test_character_system():
    print("=== INITIALIZING CHARACTER SYSTEM TEST ===")
    char = Character()
    ui = CharacterSheetUI(char)

    # 1. Attribute Allocation
    # Mocking input for automation or just skipping?
    # Let's set attributes manually for the test to avoid interactive blocking if run automatically.
    print("\n[TEST] Setting Attributes Manually...")
    char.set_attribute("REASON", 4)
    char.set_attribute("INTUITION", 5)
    char.set_attribute("CONSTITUTION", 3)
    char.set_attribute("PRESENCE", 2)
    
    # 2. Display Sheet
    print("\n[TEST] Displaying Initial Sheet...")
    ui.display()

    # 3. Leveling
    print("\n[TEST] Adding 150 XP...")
    char.add_xp(150)
    print(f"Level: {char.level} (Expected: 2)")
    print(f"Skill Points: {char.skill_points} (Expected: 1)")

    # 4. Skill Increase
    print("\n[TEST] Increasing 'Logic' skill...")
    print(f"Logic Base Before: {char.get_skill('Logic').base_level}")
    char.spend_skill_point("Logic")
    print(f"Logic Base After: {char.get_skill('Logic').base_level}")
    
    # 5. Modifiers
    print("\n[TEST] Applying Modifier to 'Logic' (+2 from 'Coffee')...")
    char.apply_modifier("Logic", "Coffee", 2)
    print(f"Logic Effective (Base 1 + 2): {char.get_skill_total('Logic')}")
    ui.display()

    # 6. Passive Interrupts
    print("\n[TEST] Testing Passive Interrupt (Context: 'A bloody knife found on the floor')...")
    # Force levels high enough to trigger for test
    char.get_skill("Forensics").base_level = 10 
    interrupts = char.check_passive_interrupts("A bloody knife found on the floor")
    if interrupts:
        for msg in interrupts:
            print(f"Interrupt: {msg}")
    else:
        print("No interrupts triggered (RNG might have failed or levels too low).")

    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_character_system()
