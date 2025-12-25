"""
Quick debug script to test lens calculation
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


class MockBoard:
    def __init__(self):
        self.theories = {}


skill_levels = {
    "Paranormal Sensitivity": 6,
    "Instinct": 5,
    "Subconscious": 5,
    "Pattern Recognition": 5,
    "Logic": 2,
    "Skepticism": 1,
    "Forensics": 2,
    "Research": 1
}

skill_system = MockSkillSystem(skill_levels)
board = MockBoard()
composer = TextComposer(skill_system, board)

# Calculate totals manually
intuition_skills = ["Paranormal Sensitivity", "Instinct", "Subconscious", "Pattern Recognition"]
reason_skills = ["Logic", "Skepticism", "Forensics", "Research"]

intuition_total = sum(skill_levels.get(s, 0) for s in intuition_skills)
reason_total = sum(skill_levels.get(s, 0) for s in reason_skills)

print(f"Intuition total: {intuition_total}")
print(f"Reason total: {reason_total}")
print(f"Difference: {intuition_total - reason_total}")

lens = composer.calculate_dominant_lens({})
print(f"Calculated lens: {lens}")
print(f"Expected: {Archetype.BELIEVER}")
