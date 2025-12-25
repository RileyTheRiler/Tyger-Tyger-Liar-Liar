import sys
import os

# Add src and src/engine to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/engine"))

from mechanics import SkillSystem, Attribute, Skill

import random
from unittest.mock import patch

def test_suppression():
    print("\n--- Test: Skill Suppression ---")
    sys = SkillSystem()
    logic = sys.get_skill("Logic")
    context = "There is a pattern here."
    
    # Case 1: Trigger success (Roll 2d6 = 12)
    with patch('random.randint', return_value=6):
        interrupt = logic.maybe_interrupt(context, sanity=100.0, current_time=0.0)
        print(f"Interrupt before suppression: {'Success' if interrupt else 'Miss'}")
    
    # Case 2: Suppressed
    sys.suppress_skill("Logic", 120, 10.0)
    with patch('random.randint', return_value=6):
        interrupt = logic.maybe_interrupt(context, sanity=100.0, current_time=20.0)
        print(f"Interrupt at T=20 (Suppressed until T=130): {'Success' if interrupt else 'Miss (Correct)'}")
    
    # Case 3: Suppression expired
    with patch('random.randint', return_value=6):
        interrupt = logic.maybe_interrupt(context, sanity=100.0, current_time=140.0)
        print(f"Interrupt at T=140 (Expired): {'Success' if interrupt else 'Success (Correct)' if interrupt else 'Miss'}")

def test_arguments():
    print("\n--- Test: Skill Arguments ---")
    sys = SkillSystem()
    
    logic = sys.get_skill("Logic")
    instinct = sys.get_skill("Instinct")
    
    # Set high levels
    logic.base_level = 5
    instinct.base_level = 5
    
    context = "The victim was clearly targeted, but you feel a strange chill."
    
    # Trigger both skills (Roll 2d6 = 12 each)
    with patch('random.randint', return_value=6):
        interrupts = sys.check_passive_interrupts(context, sanity=100.0, current_time=0.0)
    
    print(f"Interrupts count: {len(interrupts)}")
    
    if interrupts and interrupts[0].get("type") == "argument":
        print("Argument detected successfully!")
        skills_in_arg = [s['skill'] for s in interrupts[0]['skills']]
        print(f"Skills involved: {skills_in_arg}")
        
        # Test resolution
        sys.resolve_argument("Logic", "Instinct")
        print("Resolved siding with Logic.")
        
        if logic.modifiers.get("argument_winner") == 2 and instinct.modifiers.get("argument_rejected") == -1:
            print("Modifiers applied correctly.")
        else:
            print(f"ERROR: Modifiers mismatch. Logic: {logic.modifiers}, Instinct: {instinct.modifiers}")
    else:
        # Debug list of skills if no argument
        found = [i.get('skill', i.get('type')) for i in interrupts]
        print(f"Found items: {found}")
        print("ERROR: No argument detected between Logic and Instinct.")

def test_reputation():
    print("\n--- Test: Skill Reputation ---")
    sys = SkillSystem()
    skepticism = sys.get_skill("Skepticism")
    
    print(f"Initial Confidence: {skepticism.confidence_modifier}")
    
    # Two correct predictions = +1 Confidence
    sys.update_skill_reputation("Skepticism", True)
    sys.update_skill_reputation("Skepticism", True)
    print(f"Confidence after 2 successes: {skepticism.confidence_modifier}")
    
    # One failure = -1 Confidence
    sys.update_skill_reputation("Skepticism", False)
    print(f"Confidence after 1 failure: {skepticism.confidence_modifier}")
    
    if skepticism.confidence_modifier == 0:
        print("Reputation tracking working.")
    else:
        print(f"ERROR: Reputation tracking failed. Current: {skepticism.confidence_modifier}")

if __name__ == "__main__":
    test_suppression()
    test_arguments()
    test_reputation()
