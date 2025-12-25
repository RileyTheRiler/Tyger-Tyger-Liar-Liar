"""
Test script for Phase 2.1: Lens System Core Engine.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mechanics import SkillSystem
from board import Board
from lens_system import LensSystem

def test_lens():
    print("=" * 60)
    print("TESTING LENS SYSTEM CORE ENGINE")
    print("=" * 60)
    
    # Setup
    skills = SkillSystem(os.path.abspath("data/skills.json"))
    board = Board()
    lens = LensSystem(skills, board)
    
    # Sample variants
    variants = {
        "believer": "The aurora is AWARE. It's watching you.",
        "skeptic": "The aurora is just atmospheric refraction.",
    }
    base = "The aurora shimmers overhead."
    
    # Test 1: Neutral Lens
    print("\n[TEST 1] Neutral Lens (Equal stats)")
    print(f"  Current Lens: {lens.calculate_lens()}")
    print(f"  Result: {lens.filter_text(base, variants)}")
    
    # Test 2: Believer Lens (High Paranormal Sensitivity)
    print("\n[TEST 2] Believer Lens (Paranormal Sensitivity +5)")
    # Must also boost attribute because skills are capped by attribute value
    skills.attributes["INTUITION"].value = 6
    skills.get_skill("Paranormal Sensitivity").base_level = 5
    print(f"  Current Lens: {lens.calculate_lens()}")
    print(f"  Result: {lens.filter_text(base, variants)}")
    
    # Test 3: Skeptic Lens (High Logic)
    print("\n[TEST 3] Skeptic Lens (Logic +5)")
    skills.get_skill("Paranormal Sensitivity").base_level = 0
    skills.attributes["REASON"].value = 6
    skills.get_skill("Logic").base_level = 5
    print(f"  Current Lens: {lens.calculate_lens()}")
    print(f"  Result: {lens.filter_text(base, variants)}")
    
    # Test 4: Theory influence
    print("\n[TEST 4] Theory influence (I Want To Believe)")
    skills.get_skill("Logic").base_level = 0
    skills.get_skill("Paranormal Sensitivity").base_level = 0
    # Add theory
    board.theories["i_want_to_believe"].status = "active"
    print(f"  Current Lens: {lens.calculate_lens()}")
    print(f"  Result: {lens.filter_text(base, variants)}")
    
    # Test 5: Locked Lens
    print("\n[TEST 5] Locked Lens")
    lens.lock_lens("skeptic")
    skills.get_skill("Paranormal Sensitivity").base_level = 20 # Try to push it back
    print(f"  Current Lens: {lens.calculate_lens()}")
    print(f"  Result: {lens.filter_text(base, variants)}")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_lens()
