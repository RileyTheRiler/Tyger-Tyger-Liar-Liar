import random
import json
import os
from typing import Dict, List, Optional, Tuple
from dice import roll_2d6, get_roll_description

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
        
        # Phase 4 additions
        self.confidence_modifier = 0 # -2 to +2 based on reputation
        self.correct_predictions = 0
        self.incorrect_predictions = 0
        self.suppressed_until = 0.0 # Time timestamp

    @property
    def effective_level(self) -> int:
        """
        Calculates current level based on base + modifiers + confidence.
        CAPPED by the parent Attribute's value.
        """
        total = self.base_level + sum(self.modifiers.values()) + self.confidence_modifier
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
            "modifiers": dict(self.modifiers),
            "confidence_modifier": self.confidence_modifier,
            "correct_predictions": self.correct_predictions,
            "incorrect_predictions": self.incorrect_predictions,
            "suppressed_until": self.suppressed_until
        }

    def maybe_interrupt(self, context: str, sanity: float = 100.0, current_time: float = 0.0, custom_lines: List[str] = None) -> Optional[dict]:
        """
        Has a chance to interject with flavor commentary based on context.
        Likelihood increases as Sanity decreases.
        """
        # Check suppression
        if current_time < self.suppressed_until:
            return None

        # Logic: Roll 2d6 + effective_level + sanity_bonus. If > Threshold (e.g. 10), interrupt.
        roll = random.randint(1, 6) + random.randint(1, 6)
        
        # Sanity bonus: +1 for every 10 points below 100
        sanity_bonus = (100.0 - sanity) // 10
        
        if roll + self.effective_level + sanity_bonus >= 11:
            # Determine color from attribute
            attr_name = self.attribute_ref.name
            color = SkillSystem.ATTR_COLORS.get(attr_name, "white")

            if custom_lines:
                voice_text = random.choice(custom_lines)
            else:
                context_preview = context[:50].strip() + "..." if len(context) > 50 else context.strip()
                voice_text = random.choice([
                    f"\"{self.personality}\"",
                    f"\"You sense something... '{context_preview}'\"",
                    f"\"Focus on this: {self.personality}\""
                ])
            
            return {
                "skill": self.name.upper(),
                "color": color,
                "text": voice_text,
                "icon": f"icon_{self.name.lower().replace(' ', '_')}"
            }
        return None

class SkillSystem:
    # Attribute Constants
    ATTR_REASON = "REASON"
    ATTR_INTUITION = "INTUITION"
    ATTR_CONSTITUTION = "CONSTITUTION"
    ATTR_PRESENCE = "PRESENCE"

    ATTR_COLORS = {
        ATTR_REASON: "blue",
        ATTR_INTUITION: "purple",
        ATTR_CONSTITUTION: "red",
        ATTR_PRESENCE: "yellow"
    }

    CONFLICTS = {
        "Logic": ["Instinct", "Paranormal Sensitivity", "Occult Knowledge"],
        "Skepticism": ["Empathy", "Paranormal Sensitivity", "Instinct"],
        "Instinct": ["Logic", "Skepticism"],
        "Authority": ["Charm", "Empathy"],
        "Forensics": ["Occult Knowledge"]
    }
    
    def __init__(self, skills_file: Optional[str] = None):
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
        self.skills_file = skills_file
        self.interrupt_lines: Dict[str, List[str]] = {}
        self.theory_commentary: Dict[str, dict] = {}
        
        self._initialize_skills()
        self._load_interrupt_lines()
        self._load_theory_commentary()

    def _load_theory_commentary(self):
        paths = ["data/theory_commentary.json", "kaltvik_game/data/theory_commentary.json"]
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        self.theory_commentary = json.load(f)
                    break
                except Exception as e:
                    print(f"[WARNING] Could not load theory commentary from {p}: {e}")

    def _load_interrupt_lines(self):
        paths = ["data/interrupt_lines.json", "kaltvik_game/data/interrupt_lines.json"]
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        self.interrupt_lines = json.load(f)
                    break
                except Exception as e:
                    print(f"[WARNING] Could not load interrupt lines from {p}: {e}")

    def _initialize_skills(self):
        # Load from JSON if possible
        if self.skills_file and os.path.exists(self.skills_file):
            try:
                with open(self.skills_file, "r") as f:
                    metadata = json.load(f)
                
                for attr_name, skills in metadata.items():
                    attr_obj = self.attributes.get(attr_name)
                    if not attr_obj:
                        attr_obj = Attribute(attr_name)
                        self.attributes[attr_name] = attr_obj
                    
                    for skill_name, personality in skills.items():
                        self._add_skill(skill_name, attr_obj, personality)
                return
            except Exception as e:
                print(f"[WARNING] Could not load {self.skills_file}: {e}. Using fallback skills.")
        
        elif os.path.exists("data/skills.json"):
            # Fallback to local data/skills.json if no file passed but it exists
            try:
                with open("data/skills.json", "r") as f:
                    metadata = json.load(f)
                
                for attr_name, skills in metadata.items():
                    attr_obj = self.attributes.get(attr_name)
                    if not attr_obj:
                        attr_obj = Attribute(attr_name)
                        self.attributes[attr_name] = attr_obj
                    
                    for skill_name, personality in skills.items():
                        self._add_skill(skill_name, attr_obj, personality)
                return
            except Exception as e:
                print(f"[WARNING] Could not load data/skills.json: {e}. Using fallback skills.")

        # Helper to grab attr obj
        def get_attr(name): return self.attributes[name]

        # REASON (7)
        self._add_skill("Logic", get_attr(self.ATTR_REASON), "The world is a machine of cause and effect.")
        self._add_skill("Forensics", get_attr(self.ATTR_REASON), "The dead speak if you listen.")
        self._add_skill("Research", get_attr(self.ATTR_REASON), "Knowledge is hidden in the archives.")
        self._add_skill("Skepticism", get_attr(self.ATTR_REASON), "Trust nothing.")
        self._add_skill("Medicine", get_attr(self.ATTR_REASON), "The frailty of the flesh.")
        self._add_skill("Technology", get_attr(self.ATTR_REASON), "Ghosts in the machine.")
        self._add_skill("Occult Knowledge", get_attr(self.ATTR_REASON), "Things that should not be.")

        # INTUITION (7)
        self._add_skill("Pattern Recognition", get_attr(self.ATTR_INTUITION), "Everything connects.")
        self._add_skill("Paranormal Sensitivity", get_attr(self.ATTR_INTUITION), "The air feels... wrong.")
        self._add_skill("Profiling", get_attr(self.ATTR_INTUITION), "Everyone wears a mask.")
        self._add_skill("Instinct", get_attr(self.ATTR_INTUITION), "Gut feeling over facts.")
        self._add_skill("Subconscious", get_attr(self.ATTR_INTUITION), "The boundary between sleep and waking.")
        self._add_skill("Manipulation", get_attr(self.ATTR_INTUITION), "Strings attached.")
        self._add_skill("Perception", get_attr(self.ATTR_INTUITION), "The world is a tapestry.")

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
        self._add_skill("Empathy", get_attr(self.ATTR_PRESENCE), "You are a mirror of the world's pain.")
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
        dice_result = roll_2d6(manual_roll)
        roll_val = dice_result["total"]

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
            "dice": dice_result,
            "description": get_roll_description(dice_result)
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

    def check_passive_interrupts(self, context: str, sanity: float = 100.0, current_time: float = 0.0) -> List[dict]:
        interrupts = []
        for skill in self.skills.values():
            custom = self.interrupt_lines.get(skill.name)
            interrupt = skill.maybe_interrupt(context, sanity, current_time, custom_lines=custom)
            if interrupt:
                # Skill names can be double checked for capitalization in CONFLICTS
                interrupts.append(interrupt)
        
        # Argument Detection (Phase 4)
        if len(interrupts) >= 2:
            for i in range(len(interrupts)):
                for j in range(i + 1, len(interrupts)):
                    s1 = interrupts[i]["skill"].title()
                    s2 = interrupts[j]["skill"].title()
                    
                    if s2 in self.CONFLICTS.get(s1, []) or s1 in self.CONFLICTS.get(s2, []):
                        # We turn this into an argument event
                        return [{
                            "type": "argument",
                            "skills": [interrupts[i], interrupts[j]],
                            "text": f"{s1} and {s2} are at odds over this."
                        }]
        
        return interrupts

    def check_theory_commentary(self, active_theories: List[str]) -> List[dict]:
        """
        Returns a list of commentary objects for the given active theories.
        """
        commentary = []
        for tid in active_theories:
            if tid in self.theory_commentary:
                commentary.append(self.theory_commentary[tid])
        return commentary

    def resolve_argument(self, chosen_skill_name: str, rejected_skill_name: str):
        """Applies temporary modifiers based on argument resolution."""
        chosen = self.get_skill(chosen_skill_name.title())
        rejected = self.get_skill(rejected_skill_name.title())
        
        if chosen:
            chosen.set_modifier("argument_winner", 2)
        if rejected:
            rejected.set_modifier("argument_rejected", -1)
            
    def update_skill_reputation(self, skill_name: str, correct: bool):
        """Adjusts skill confidence based on outcome."""
        skill = self.get_skill(skill_name.title())
        if not skill: return
        
        if correct:
            skill.correct_predictions += 1
            if skill.correct_predictions % 2 == 0:
                skill.confidence_modifier = min(2, skill.confidence_modifier + 1)
        else:
            skill.incorrect_predictions += 1
            skill.confidence_modifier = max(-2, skill.confidence_modifier - 1)

    def suppress_skill(self, skill_name: str, duration_minutes: int, current_time: float):
        """Silences a skill for a set duration."""
        skill = self.get_skill(skill_name.title())
        if skill:
            skill.suppressed_until = current_time + duration_minutes
            return True
        return False

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
    
    def apply_temporary_pov(self, skills_data: Dict[str, int]):
        """Sets skill levels for a POV shift. Typically used in flashbacks."""
        for name, level in skills_data.items():
            skill = self.get_skill(name.title())
            if skill:
                skill.base_level = level

    def load_state_from_dict(self, data: dict):
        """Restores full state from a dictionary (reverses to_dict)."""
        self.xp = data.get("xp", 0)
        self.level = data.get("level", 1)
        self.skill_points = data.get("skill_points", 0)
        self.check_history = data.get("check_history", {})
        self.failures_log = data.get("failures_log", [])
        
        # Restore attributes
        for name, attr_data in data.get("attributes", {}).items():
            if name in self.attributes:
                self.attributes[name].value = attr_data["value"]
                self.attributes[name].cap = attr_data["cap"]

        # Restore skills
        for name, skill_data in data.get("skills", {}).items():
            if name in self.skills:
                s = self.skills[name]
                s.base_level = skill_data["base_level"]
                s.modifiers = skill_data.get("modifiers", {})
                s.confidence_modifier = skill_data.get("confidence_modifier", 0)
                s.correct_predictions = skill_data.get("correct_predictions", 0)
                s.incorrect_predictions = skill_data.get("incorrect_predictions", 0)
                s.suppressed_until = skill_data.get("suppressed_until", 0.0)

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
            skill.confidence_modifier = skill_data.get("confidence_modifier", 0)
            skill.correct_predictions = skill_data.get("correct_predictions", 0)
            skill.incorrect_predictions = skill_data.get("incorrect_predictions", 0)
            skill.suppressed_until = skill_data.get("suppressed_until", 0.0)
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

                eff_uncapped = base + mod_sum + skill.confidence_modifier
                is_capped = effective < eff_uncapped
                cap_mark = " [CAPPED]" if is_capped else ""
                
                # Phase 4: Status / Reputation
                conf = skill.confidence_modifier
                rep = "RELIABLE" if conf >= 1 else "SHAKEN" if conf <= -1 else "NEUTRAL"
                if skill.suppressed_until > 0: # We'd need current_time here, but simple check for now
                     rep += " (SUPPRESSED)"
                
                print(f"  {skill.name.ljust(22)} : {effective}{mod_str}{cap_mark} [{rep}]")

        print(f"{'='*40}\n")
