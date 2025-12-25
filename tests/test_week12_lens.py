"""
Test Week 12: Lens Filtering
Tests dynamic lens calculation based on skills and theories.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.text_composer import TextComposer, Archetype


class MockSkill:
    def __init__(self, level):
        self.effective_level = level


class MockSkillSystem:
    def __init__(self, skill_levels):
        self.skill_levels = skill_levels
    
    def get_skill(self, name):
        if name in self.skill_levels:
            return MockSkill(self.skill_levels[name])
        return None


class MockTheory:
    def __init__(self, theory_id, status="active"):
        self.id = theory_id
        self.status = status


class MockBoard:
    def __init__(self, active_theory_ids=None):
        self.theories = {}
        if active_theory_ids:
            for tid in active_theory_ids:
                self.theories[tid] = MockTheory(tid, "active")


def test_intuition_dominant():
    """Test lens calculation with Intuition-dominant character."""
    print("Testing Intuition-dominant lens...")
    
    skill_levels = {
        "Paranormal Sensitivity": 6,
        "Instinct": 5,
        "Subconscious": 5,
        "Pattern Recognition": 5,  # Total: 21
        "Logic": 2,
        "Skepticism": 1,
        "Forensics": 2,
        "Research": 1  # Total: 6
    }
    
    skill_system = MockSkillSystem(skill_levels)
    board = MockBoard()
    composer = TextComposer(skill_system, board)
    
    lens = composer.calculate_dominant_lens({})
    
    assert lens == Archetype.BELIEVER, f"Expected BELIEVER, got {lens}"
    print(f"  ✓ Intuition-dominant correctly identified as {lens.value}")


def test_reason_dominant():
    """Test lens calculation with Reason-dominant character."""
    print("Testing Reason-dominant lens...")
    
    skill_levels = {
        "Paranormal Sensitivity": 1,
        "Instinct": 2,
        "Subconscious": 1,
        "Pattern Recognition": 2,
        "Logic": 5,
        "Skepticism": 5,
        "Forensics": 4,
        "Research": 4
    }
    
    skill_system = MockSkillSystem(skill_levels)
    board = MockBoard()
    composer = TextComposer(skill_system, board)
    
    lens = composer.calculate_dominant_lens({})
    
    assert lens == Archetype.SKEPTIC, f"Expected SKEPTIC, got {lens}"
    print(f"  ✓ Reason-dominant correctly identified as {lens.value}")


def test_theory_override():
    """Test that active theories override skill-based lens."""
    print("Testing theory override...")
    
    # Reason-dominant skills
    skill_levels = {
        "Logic": 5,
        "Skepticism": 5,
        "Forensics": 4,
        "Research": 4,
        "Paranormal Sensitivity": 1,
        "Instinct": 1
    }
    
    skill_system = MockSkillSystem(skill_levels)
    
    # But believer theory active
    board = MockBoard(["The Truth Is Out There"])
    composer = TextComposer(skill_system, board)
    
    lens = composer.calculate_dominant_lens({})
    
    assert lens == Archetype.BELIEVER, f"Expected BELIEVER from theory override, got {lens}"
    print(f"  ✓ Theory override working: {lens.value}")


def test_haunted_theory():
    """Test haunted archetype from specific theories."""
    print("Testing haunted theory...")
    
    skill_levels = {"Logic": 3, "Skepticism": 3}
    skill_system = MockSkillSystem(skill_levels)
    board = MockBoard(["I've Been Here Before"])
    composer = TextComposer(skill_system, board)
    
    lens = composer.calculate_dominant_lens({})
    
    assert lens == Archetype.HAUNTED, f"Expected HAUNTED, got {lens}"
    print(f"  ✓ Haunted theory correctly identified: {lens.value}")


def test_neutral_lens():
    """Test neutral lens when skills are balanced."""
    print("Testing neutral lens...")
    
    skill_levels = {
        "Paranormal Sensitivity": 3,
        "Instinct": 3,
        "Logic": 3,
        "Skepticism": 3
    }
    
    skill_system = MockSkillSystem(skill_levels)
    board = MockBoard()
    composer = TextComposer(skill_system, board)
    
    lens = composer.calculate_dominant_lens({})
    
    assert lens == Archetype.NEUTRAL, f"Expected NEUTRAL, got {lens}"
    print(f"  ✓ Balanced skills correctly identified as {lens.value}")


if __name__ == "__main__":
    print("Running Week 12 Lens Filtering Tests...")
    print("=" * 50)
    print()
    
    test_intuition_dominant()
    test_reason_dominant()
    test_theory_override()
    test_haunted_theory()
    test_neutral_lens()
    
    print()
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
