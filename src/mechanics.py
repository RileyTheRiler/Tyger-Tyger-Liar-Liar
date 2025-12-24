import random
from typing import Dict, List, Optional, Tuple

class Attribute:
    def __init__(self, name: str, base_value: int = 1, cap: int = 6):
        self.name = name
        self._value = base_value
        self.cap = cap

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        self._value = min(max(new_val, 1), self.cap)
    
    def to_dict(self) -> dict:
        """Serialize attribute to dictionary."""
        return {
            "name": self.name,
            "value": self._value,
            "cap": self.cap
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Attribute':
        """Deserialize attribute from dictionary."""
        attr = Attribute(data["name"], data["value"], data["cap"])
        return attr

class Skill:
    def __init__(self, name: str, attribute_obj: Attribute, personality_desc: str):
        self.name = name
        self.attribute_ref = attribute_obj
        self.personality = personality_desc
        self.base_level = 0
        self.modifiers: Dict[str, int] = {}

    @property
    def effective_level(self) -> int:
        """
        Calculates current level based on base + modifiers.
        CAPPED by the parent Attribute's value.
        """
        total = self.base_level + sum(self.modifiers.values())
        uncapped = max(0, total)
        # Cap by attribute value
        return min(uncapped, self.attribute_ref.value)

    def set_modifier(self, source: str, value: int):
        """Sets a modifier from a specific source. Use value=0 to remove it."""
        if value == 0:
            if source in self.modifiers:
                del self.modifiers[source]
        else:
            self.modifiers[source] = value
    
    def to_dict(self) -> dict:
        """Serialize skill to dictionary."""
        return {
            "name": self.name,
            "attribute_name": self.attribute_ref.name,
            "personality": self.personality,
            "base_level": self.base_level,
            "modifiers": dict(self.modifiers)
        }

    def maybe_interrupt(self, context: str, sanity: float = 100.0) -> Optional[str]:
        """
        Has a chance to interject with flavor commentary based on context.
        Likelihood increases as Sanity decreases.
        """
        # Logic: Roll 2d6 + effective_level + sanity_bonus. If > Threshold (e.g. 10), interrupt.
        roll = random.randint(1, 6) + random.randint(1, 6)
        
        # Sanity bonus: +1 for every 10 points below 100
        sanity_bonus = (100.0 - sanity) // 10
        
        if roll + self.effective_level + sanity_bonus >= 11:
            # Avoid repeating massive context strings
            context_preview = context[:50].strip() + "..." if len(context) > 50 else context.strip()
            
            voices = [
                f"[{self.name.upper()}] \"{self.personality}\"",
                f"[{self.name.upper()}] \"You sense something... '{context_preview}'\"",
                f"[{self.name.upper()}] \"Focus on this: {self.personality}\""
            ]
            return random.choice(voices)
        return None

class SkillSystem:
    # Attribute Constants
    ATTR_REASON = "REASON"
    ATTR_INTUITION = "INTUITION"
    ATTR_CONSTITUTION = "CONSTITUTION"
    ATTR_PRESENCE = "PRESENCE"

    
    def __init__(self):
        self.attributes: Dict[str, Attribute] = {
            self.ATTR_REASON: Attribute(self.ATTR_REASON, base_value=1),
            self.ATTR_INTUITION: Attribute(self.ATTR_INTUITION, base_value=1),
            self.ATTR_CONSTITUTION: Attribute(self.ATTR_CONSTITUTION, base_value=1),
            self.ATTR_PRESENCE: Attribute(self.ATTR_PRESENCE, base_value=1),
        }
        
        self.skills: Dict[str, Skill] = {}
        self.xp = 0
        self.level = 1
        self.skill_points = 0
        self.check_history: Dict[str, dict] = {}
        self.failures_log: List[dict] = []
        
        self._initialize_skills()

    def _initialize_skills(self):
        # Helper to grab attr obj
        def get_attr(name): return self.attributes[name]

        # REASON (7)
        self._add_skill("Logic", get_attr(self.ATTR_REASON), "Cold, deductible facts.")
        self._add_skill("Forensics", get_attr(self.ATTR_REASON), "The dead speak if you listen.")
        self._add_skill("Research", get_attr(self.ATTR_REASON), "Knowledge is hidden in the archives.")
        self._add_skill("Skepticism", get_attr(self.ATTR_REASON), "Trust nothing.")
        self._add_skill("Medicine", get_attr(self.ATTR_REASON), "The frailty of the flesh.")
        self._add_skill("Technology", get_attr(self.ATTR_REASON), "Ghosts in the machine.")
        self._add_skill("Occult Knowledge", get_attr(self.ATTR_REASON), "Things that should not be.")

        # INTUITION (7)
        self._add_skill("Pattern Recognition", get_attr(self.ATTR_INTUITION), "Everything connects.")
        self._add_skill("Paranormal Sensitivity", get_attr(self.ATTR_INTUITION), "The air feels... wrong.")
        self._add_skill("Profiling", get_attr(self.ATTR_INTUITION), "People are open books.")
        self._add_skill("Instinct", get_attr(self.ATTR_INTUITION), "Gut feeling over facts.")
        self._add_skill("Subconscious", get_attr(self.ATTR_INTUITION), "Dreams are reality.")
        self._add_skill("Manipulation", get_attr(self.ATTR_INTUITION), "Strings attached.")
        self._add_skill("Perception", get_attr(self.ATTR_INTUITION), "Eyes wide open.")

        # CONSTITUTION (8)
        self._add_skill("Endurance", get_attr(self.ATTR_CONSTITUTION), "Pain is just information.")
        self._add_skill("Fortitude", get_attr(self.ATTR_CONSTITUTION), "Unbreakable.")
        self._add_skill("Firearms", get_attr(self.ATTR_CONSTITUTION), "Loud conflict resolution.")
        self._add_skill("Athletics", get_attr(self.ATTR_CONSTITUTION), "Motion is life.")
        self._add_skill("Stealth", get_attr(self.ATTR_CONSTITUTION), "Unseen, unheard.")
        self._add_skill("Reflexes", get_attr(self.ATTR_CONSTITUTION), "Faster than thought.")
        self._add_skill("Survival", get_attr(self.ATTR_CONSTITUTION), "Live another day.")
        self._add_skill("Hand-to-Hand Combat", get_attr(self.ATTR_CONSTITUTION), "Up close and personal.")

        # PRESENCE (7)
        self._add_skill("Authority", get_attr(self.ATTR_PRESENCE), "Obey.")
        self._add_skill("Charm", get_attr(self.ATTR_PRESENCE), "A smile opens doors.")
        self._add_skill("Wits", get_attr(self.ATTR_PRESENCE), "Sharp tongue.")
        self._add_skill("Composure", get_attr(self.ATTR_PRESENCE), "Never let them see you sweat.")
        self._add_skill("Empathy", get_attr(self.ATTR_PRESENCE), "I feel your pain.")
        self._add_skill("Interrogation", get_attr(self.ATTR_PRESENCE), "Truth hurts.")
        self._add_skill("Deception", get_attr(self.ATTR_PRESENCE), "A lie is a constructed truth.")

    def _add_skill(self, name: str, attribute_obj: Attribute, personality: str):
        self.skills[name] = Skill(name, attribute_obj, personality)

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        return self.skills.get(skill_name)
    
    def get_skill_total(self, skill_name: str) -> int:
        s = self.get_skill(skill_name)
        return s.effective_level if s else 0

    def increase_skill(self, skill_name: str, amount: int = 1):
        s = self.get_skill(skill_name)
        if s:
            s.base_level += amount

    def roll_check(self, skill_name: str, difficulty: int, check_type: str = "white", check_id: str = None, manual_roll: int = None) -> dict:
        """
        Executes a 2d6 skill check.
        Supports Red/White checks logic with retry handling.
        """
        # Default check_id fallback
        if not check_id:
            check_id = f"auto_{skill_name}_{difficulty}_{random.randint(1000,9999)}"

        skill = self.get_skill(skill_name)
        effective_level = skill.effective_level if skill else 0

        # --- RETRY LOGIC CHECKS ---
        if check_id in self.check_history:
             prev = self.check_history[check_id]
             
             # If already succeeded
             if prev["success"]:
                 return {
                     "skill": skill_name, "roll": prev["roll"], "total": prev["total"],
                     "success": True, "type": check_type, "msg": "Already succeeded."
                 }
             
             # Block Red Check Retry
             if prev["type"] == "red":
                 return {
                     "success": False, "blocked": True,
                     "msg": "Red Check failure is permanent.", "type": "red"
                 }
                 
             # Block White Check Retry if skill hasn't improved
             if check_type == "white":
                 if effective_level <= prev["skill_level_at_attempt"]:
                     return {
                         "success": False, "blocked": True,
                         "msg": "Skill too low to retry. Raise skill level to attempt again.",
                         "type": "white"
                     }

        # --- PERFORM ROLL ---
        if manual_roll is not None:
            roll_val = manual_roll
        else:
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            roll_val = d1 + d2

        total = roll_val + effective_level
        success = total >= difficulty

        result = {
            "skill": skill_name,
            "roll": roll_val,
            "modifier": effective_level,
            "total": total,
            "difficulty": difficulty,
            "success": success,
            "type": check_type,
            "blocked": False,
            "skill_level_at_attempt": effective_level,
            "die_rolls": [manual_roll] if manual_roll else [d1, d2] # approximate for manual
        }
        
        # --- RECORD HISTORY ---
        self.check_history[check_id] = result
        if not success:
             self.failures_log.append({
                 "check_id": check_id,
                 "skill": skill_name,
                 "type": check_type,
                 "time": "now" # Placeholder for time system integration
             })

        return result

    def check_passive_interrupts(self, context: str, sanity: float = 100.0) -> List[str]:
        interrupts = []
        for skill in self.skills.values():
            msg = skill.maybe_interrupt(context, sanity)
            if msg:
                interrupts.append(msg)
        return interrupts

    # Leveling System
    def add_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.level * 100:
             self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1 
        print(f"[LEVEL UP!] You are now level {self.level}. Skill Points: {self.skill_points}")

    def spend_point(self, skill_name: str):
        if self.skill_points > 0:
            skill = self.skills.get(skill_name)
            if skill:
                 if skill.base_level < skill.attribute_ref.value:
                     skill.base_level += 1
                     self.skill_points -= 1
                     print(f"[{skill_name} increased to {skill.base_level}]")
                 else:
                     print(f"Cannot raise {skill_name}: Capped by {skill.attribute_ref.name} ({skill.attribute_ref.value})")
        else:
            print("No skill points available.")
    
    def to_dict(self) -> dict:
        """Serialize skill system to dictionary."""
        return {
            "attributes": {name: attr.to_dict() for name, attr in self.attributes.items()},
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "xp": self.xp,
            "level": self.level,
            "skill_points": self.skill_points,
            "check_history": self.check_history,
            "failures_log": self.failures_log
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'SkillSystem':
        """Deserialize skill system from dictionary."""
        system = SkillSystem()
        
        # Restore attributes
        for name, attr_data in data.get("attributes", {}).items():
            system.attributes[name] = Attribute.from_dict(attr_data)
        
        # Restore skills - need to reconnect attribute references
        for name, skill_data in data.get("skills", {}).items():
            attr_name = skill_data["attribute_name"]
            attr_obj = system.attributes[attr_name]
            skill = Skill(skill_data["name"], attr_obj, skill_data["personality"])
            skill.base_level = skill_data["base_level"]
            skill.modifiers = skill_data.get("modifiers", {})
            system.skills[name] = skill
        
        system.xp = data.get("xp", 0)
        system.level = data.get("level", 1)
        system.skill_points = data.get("skill_points", 0)
        system.check_history = data.get("check_history", {})
        system.failures_log = data.get("failures_log", [])
        
        return system

class CharacterSheetUI:
    def __init__(self, system: SkillSystem):
        self.sys = system

    def display(self):
        print(f"\n{'='*40}")
        print(f" CHARACTER SHEET")
        print(f" LEVEL: {self.sys.level} | XP: {self.sys.xp} | SP: {self.sys.skill_points}")
        print(f"{'='*40}")

        # Helper to get skills for an attribute
        def get_skills_for_attr(attr_name):
            return [s for s in self.sys.skills.values() if s.attribute_ref.name == attr_name]

        for attr_key in [self.sys.ATTR_REASON, self.sys.ATTR_INTUITION, self.sys.ATTR_CONSTITUTION, self.sys.ATTR_PRESENCE]:
            attr = self.sys.attributes[attr_key]
            print(f"\n[{attr.name.ljust(12)}: {attr.value}/{attr.cap}]")
            print("-" * 40)
            
            for skill in get_skills_for_attr(attr_key):
                effective = skill.effective_level
                base = skill.base_level
                
                mod_str = ""
                mod_sum = sum(skill.modifiers.values())
                if mod_sum != 0:
                     sign = "+" if mod_sum > 0 else ""
                     mod_str = f" ({sign}{mod_sum})"

                eff_uncapped = base + mod_sum
                is_capped = effective < eff_uncapped
                cap_mark = " [CAPPED]" if is_capped else ""
                
                print(f"  {skill.name.ljust(22)} : {effective}{mod_str}{cap_mark}")

        print(f"{'='*40}\n")
