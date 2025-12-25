from typing import Dict, Optional
from tyger_game.utils.constants import ATTRIBUTES, SKILLS, MAX_SANITY, MAX_REALITY

class Character:
    def __init__(self, name: str = "Detective"):
        self.name = name
        
        # Attributes (Default to 3 - Average/Competent)
        self.attributes: Dict[str, int] = {attr: 3 for attr in ATTRIBUTES}
        
        # Skills (Base level 0, effective level = base + attribute)
        # Stored as {skill_name: base_level}
        self.skills: Dict[str, int] = {}
        self._init_skills()

        # Resources
        self.sanity: int = MAX_SANITY
        self.reality: int = MAX_REALITY
        
        # Experience / Internalization
        self.xp: int = 0
        self.thoughts: list = []
        self.inventory: list = []

    def _init_skills(self):
        """Initialize all skills to base 0."""
        for attr, skill_list in SKILLS.items():
            for skill in skill_list:
                self.skills[skill] = 0

    def get_skill_level(self, skill_name: str) -> int:
        """
        Calculates effective skill level:
        Base Skill + Parent Attribute Value + Modifiers (TODO)
        """
        # Find parent attribute
        parent_attr = None
        for attr, s_list in SKILLS.items():
            if skill_name in s_list:
                parent_attr = attr
                break
        
        if not parent_attr:
            raise ValueError(f"Skill {skill_name} not found.")

        attr_val = self.attributes[parent_attr]
        base_val = self.skills.get(skill_name, 0)
        
        modifier_val = 0
        
        # Item modifiers
        for item in self.inventory:
            # Check if item has get_skill_modifier method (e.g. Item class from src.inventory_system)
            if hasattr(item, 'get_skill_modifier'):
                modifier_val += item.get_skill_modifier(skill_name)
            # Fallback for dict-like items or simplified objects
            elif hasattr(item, 'effects') and isinstance(item.effects, dict):
                 mods = item.effects.get("skill_modifiers", {})
                 modifier_val += mods.get(skill_name, 0)

        # Thought modifiers
        for thought in self.thoughts:
            # Check thought state (e.g. Thought class from src.thoughts)
            is_active = getattr(thought, 'is_active', False)
            is_internalized = getattr(thought, 'is_internalized', False)

            if is_active:
                temp_effects = getattr(thought, 'temporary_effects', {})
                modifier_val += temp_effects.get(skill_name, 0)

            if is_internalized:
                perm_effects = getattr(thought, 'permanent_effects', {})
                modifier_val += perm_effects.get(skill_name, 0)

        return attr_val + base_val + modifier_val

    def modify_sanity(self, amount: int):
        self.sanity = max(0, min(MAX_SANITY, self.sanity + amount))

    def modify_reality(self, amount: int):
        self.reality = max(0, min(MAX_REALITY, self.reality + amount))

    def __str__(self):
        return f"{self.name} | Sanity: {self.sanity} | Reality: {self.reality}"
