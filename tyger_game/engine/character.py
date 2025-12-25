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
        
        # Epistemic Alignment
        # Tracks the raw score for each axis pole
        self.alignment_scores: Dict[str, int] = {
            "believer": 0,
            "skeptic": 0,
            "order": 0,
            "chaos": 0
        }
        self.active_alignment: Optional[str] = None # e.g. "Fundamentalist"

        # Experience / Internalization
        self.xp: int = 0
        # Paradigms (Conspiracy/Philosophy Thoughts)
        # Format: {"id": "simulation_hypothesis", "status": "internalizing", "progress": 0, "completed": False}
        self.paradigms: list = [] 
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
        
        # TODO: Add item/thought modifiers here
        
        return attr_val + base_val

    def modify_sanity(self, amount: int):
        self.sanity = max(0, min(MAX_SANITY, self.sanity + amount))

    def modify_reality(self, amount: int):
        self.reality = max(0, min(MAX_REALITY, self.reality + amount))

    def __str__(self):
        return f"{self.name} | Sanity: {self.sanity} | Reality: {self.reality}"
