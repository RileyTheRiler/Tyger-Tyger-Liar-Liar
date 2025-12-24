import random
from typing import List, Dict, Tuple, Optional

class Attribute:
    def __init__(self, name: str, value: int = 1, cap: int = 6):
        self.name = name
        self._value = value
        self.cap = cap

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value > self.cap:
            self._value = self.cap
        elif new_value < 1:
            self._value = 1
        else:
            self._value = new_value

class Skill:
    def __init__(self, name: str, attribute_name: str, personality_desc: str):
        self.name = name
        self.attribute_name = attribute_name
        self.personality_desc = personality_desc
        self.base_level = 0
        self.modifiers: List[Tuple[str, int]] = []  # (source, value)

    def get_effective_level(self, parent_attribute_value: int) -> int:
        total = self.base_level + sum(val for _, val in self.modifiers)
        # Cap logic: Effective level cannot exceed parent attribute (as per prompt?)
        # "effective_level: computed property capped by its parent attribute"
        return min(max(total, 0), parent_attribute_value)

    def apply_modifier(self, source: str, value: int):
        self.modifiers.append((source, value))

    def remove_modifier(self, source: str):
        self.modifiers = [mod for mod in self.modifiers if mod[0] != source]

    def maybe_interrupt(self, context: str, current_level: int, sanity: int = 100) -> Optional[str]:
        """
        Takes a narrative context.
        Has a chance to interject with flavor commentary.
        Uses randomness + skill level + sanity inverse to determine likelihood.
        """
        # Base DC starts at 15
        # Skill level helps (e.g. level 5 adds 5)
        # Low Sanity helps trigger (sanity < 50 adds bonus to roll)
        
        roll = random.randint(1, 20)
        
        sanity_bonus = 0
        if sanity < 50:
            sanity_bonus = (50 - sanity) // 5  # +1 for every 5 points below 50
            
        total = roll + current_level + sanity_bonus
        
        if total >= 15:
            return f"[{self.name.upper()}]: \"{self.personality_desc} regarding '{context}'\""
        return None

class Character:
    def __init__(self, name: str = "Protagonist"):
        self.name = name
        self.xp = 0
        self.level = 1
        self.skill_points = 0
        
        # Psychological Stats
        self.sanity = 100
        self.reality = 100
        self.mental_conditions: List[Dict] = []
        
        # Attributes
        self.attributes: Dict[str, Attribute] = {
            "REASON": Attribute("REASON", 1),
            "INTUITION": Attribute("INTUITION", 1),
            "CONSTITUTION": Attribute("CONSTITUTION", 1),
            "PRESENCE": Attribute("PRESENCE", 1)
        }

        # Skills Mapping
        skill_definitions = {
            "REASON": [
                ("Logic", "Cold, deductible facts."),
                ("Forensics", "The dead speak if you listen."),
                ("Research", "Knowledge is hidden in the archives."),
                ("Skepticism", "Trust nothing."),
                ("Medicine", " The frailty of the flesh."),
                ("Technology", "Ghosts in the machine."),
                ("Occult Knowledge", "Things that should not be.")
            ],
            "INTUITION": [
                ("Pattern Recognition", "Everything connects."),
                ("Paranormal Sensitivity", "The air feels... wrong."),
                ("Profiling", "People are open books."),
                ("Instinct", "Gut feeling over facts."),
                ("Subconscious", "Dreams are reality."),
                ("Manipulation", "Strings attached."),
                ("Perception", "Eyes wide open.")
            ],
            "CONSTITUTION": [
                ("Endurance", "Pain is just information."),
                ("Fortitude", "Unbreakable."),
                ("Firearms", "Loud conflict resolution."),
                ("Athletics", "Motion is life."),
                ("Stealth", "Unseen, unheard."),
                ("Reflexes", "Faster than thought."),
                ("Survival", "Live another day."),
                ("Hand-to-Hand Combat", "Up close and personal.")
            ],
            "PRESENCE": [
                ("Authority", "Obey."),
                ("Charm", "A smile opens doors."),
                ("Wits", "Sharp tongue."),
                ("Composure", "Never let them see you sweat."),
                ("Empathy", "I feel your pain."),
                ("Interrogation", "Truth hurts."),
                ("Deception", "A lie is a constructed truth.")
            ]
        }

        self.skills: Dict[str, Skill] = {}
        for attr_name, skills_list in skill_definitions.items():
            for skill_name, personality in skills_list:
                self.skills[skill_name] = Skill(skill_name, attr_name, personality)

        # Settings
        self.passive_interjections_enabled = True

    def set_attribute(self, attr_name: str, value: int):
        if attr_name in self.attributes:
            self.attributes[attr_name].value = value

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        return self.skills.get(skill_name)

    def get_skill_total(self, skill_name: str) -> int:
        skill = self.skills.get(skill_name)
        if not skill:
            return 0
        attr_val = self.attributes[skill.attribute_name].value
        return skill.get_effective_level(attr_val)

    def increase_skill(self, skill_name: str, amount: int = 1):
        skill = self.skills.get(skill_name)
        if skill:
            skill.base_level += amount

    def apply_modifier(self, skill_name: str, source: str, value: int):
        skill = self.skills.get(skill_name)
        if skill:
            skill.apply_modifier(source, value)

    def modify_sanity(self, amount: int, source: str = "Unknown"):
        old_val = self.sanity
        self.sanity = max(0, min(100, self.sanity + amount))
        diff = self.sanity - old_val
        if diff != 0:
            print(f"[SANITY {'+' if diff > 0 else ''}{diff} ({self.sanity}%)]")
            if self.sanity <= 0:
                print(">> MENTAL BREAKDOWN IMMINENT <<")

    def modify_reality(self, amount: int, source: str = "Unknown"):
        old_val = self.reality
        self.reality = max(0, min(100, self.reality + amount))
        diff = self.reality - old_val
        if diff != 0:
            print(f"[REALITY {'+' if diff > 0 else ''}{diff} ({self.reality}%)]")
            if self.reality <= 0:
                print(">> REALITY FRACTURE DETECTED <<")

    def get_psych_status(self) -> Tuple[str, str]:
        # Sanity Status
        if self.sanity >= 75: san_stat = "Stable"
        elif self.sanity >= 50: san_stat = "Unsettled"
        elif self.sanity >= 25: san_stat = "Hysteria"
        else: san_stat = "Psychosis"
        
        # Reality Status
        if self.reality >= 75: real_stat = "Lucid"
        elif self.reality >= 50: real_stat = "Doubt"
        elif self.reality >= 25: real_stat = "Delusion"
        else: real_stat = "Broken"
        
        return san_stat, real_stat

    def add_xp(self, amount: int):
        self.xp += amount
        # Check for level up
        # "Every 100 XP: gain skill points"
        # "No scaling XP requirements"
        # Since it's linear, we can just check thresholds.
        # But if we gain 200 XP at once, we should level up twice.
        while self.xp >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1 # Or however many points per level
        print(f"\n[LEVEL UP! You are now level {self.level}. Skill Points: {self.skill_points}]")

    def spend_skill_point(self, skill_name: str):
        if self.skill_points > 0:
            skill = self.skills.get(skill_name)
            if skill:
                # Check cap?
                current = self.get_skill_total(skill_name)
                attr_val = self.attributes[skill.attribute_name].value
                if skill.base_level < attr_val: # Or explicitly check if effective level is capped?
                    # The prompt says attribute cap sets max skill levels.
                    # Does base level get capped, or effective level?
                    # "effective_level: computed property capped by its parent attribute"
                    # Usually means you can't *benefit* from more, but maybe you can *have* more base?
                    # Assuming we shouldn't let base exceed cap either for sanity.
                    if skill.base_level < attr_val:
                        skill.base_level += 1
                        self.skill_points -= 1
                        print(f"[{skill_name} increased to {skill.base_level}]")
                    else:
                        print(f"Cannot increase {skill_name}: Capped by {skill.attribute_name} ({attr_val})")
                else:
                    print(f"Skill {skill_name} not found.")
        else:
            print("Not enough skill points.")

    def check_passive_interrupts(self, narrative_context: str) -> List[str]:
        if not self.passive_interjections_enabled:
            return []
        
        interrupts = []
        for skill in self.skills.values():
            effective = self.get_skill_total(skill.name)
            msg = skill.maybe_interrupt(narrative_context, effective, self.sanity)
            if msg:
                interrupts.append(msg)
        return interrupts

class CharacterSheetUI:
    def __init__(self, character: Character):
        self.character = character

    def display(self):
        c = self.character
        print(f"\n{'='*40}")
        print(f" CHARACTER SHEET: {c.name}")
        san_status, real_status = c.get_psych_status()
        print(f" SANITY: {c.sanity}% ({san_status}) | REALITY: {c.reality}% ({real_status})")
        print(f" LEVEL: {c.level} | XP: {c.xp} | SP: {c.skill_points}")
        print(f"{'='*40}")

        # Group skills by attribute
        skills_by_attr = {attr: [] for attr in c.attributes}
        for skill in c.skills.values():
            skills_by_attr[skill.attribute_name].append(skill)

        for attr_name, attr_obj in c.attributes.items():
            print(f"\n[{attr_name.ljust(12)}: {attr_obj.value}/{attr_obj.cap}]")
            print("-" * 40)
            
            current_skills = skills_by_attr[attr_name]
            # Print in 2 columns if possible, but linear is safer for text UI
            for skill in current_skills:
                effective = c.get_skill_total(skill.name)
                # Highlight modified
                mod_str = ""
                if skill.modifiers:
                    mod_sum = sum(m[1] for m in skill.modifiers)
                    if mod_sum != 0:
                        sign = "+" if mod_sum > 0 else ""
                        mod_str = f" ({sign}{mod_sum})"
                
                # Check if capped
                cap_warning = ""
                if skill.base_level > effective: # This means base calculation was capped
                    # Wait, effective is base + mods, capped.
                    # If base=5, attr=4, effective=4.
                    pass 
                
                print(f"  {skill.name.ljust(22)} : {effective}{mod_str}")

        print(f"\n[Passive Interjections: {'ON' if c.passive_interjections_enabled else 'OFF'}]")
        print(f"{'='*40}\n")

    def prompt_attribute_allocation(self, total_points=12):
        print("\n--- CHARACTER CREATION ---")
        print(f"Distribute {total_points} points among attributes (Min 1, Max 6).")
        remaining = total_points
        
        # Reset to 1s
        for attr in self.character.attributes.values():
            attr.value = 1
            remaining -= 1 # Cost for base 1? Usually point buy starts at base.
            # Let's assume points are *added* to base 1?
            # Or points *set* the value?
            # "Prompt the player to assign points to attributes (within limits)"
            # Let's do simple: Point buy. Start at 1. Costs 1 point to increase by 1.
        
        # Actually, let's just make it simple.
        # Loop through attributes.
        attrs_list = list(self.character.attributes.keys())
        
        while remaining > 0:
            print(f"\nPoints Remaining: {remaining}")
            for i, attr in enumerate(attrs_list):
                 print(f"{i+1}. {attr}: {self.character.attributes[attr].value}")
            
            try:
                choice = int(input("Select attribute to increase (1-4) or 0 to finish: "))
                if choice == 0:
                    break
                if 1 <= choice <= 4:
                    attr_name = attrs_list[choice-1]
                    attr = self.character.attributes[attr_name]
                    if attr.value < attr.cap:
                        attr.value += 1
                        remaining -= 1
                    else:
                        print("Attribute at cap!")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Enter a number.")

        print("Attribute allocation complete.")

    def run_menu(self):
        while True:
            print("\n[C]haracter Sheet | [T]oggle Passives | [E]xit Menu")
            cmd = input(">> ").lower()
            if cmd == 'c':
                self.display()
            elif cmd == 't':
                self.character.passive_interjections_enabled = not self.character.passive_interjections_enabled
                print(f"Passive interjections set to {self.character.passive_interjections_enabled}")
            elif cmd == 'e':
                break
