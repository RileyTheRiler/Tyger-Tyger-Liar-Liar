from src.skills import SkillSystem
from src.thoughts import ThoughtCabinet

class GameState:
    def __init__(self):
        # Meters
        self.sanity = 100
        self.max_sanity = 100
        self.reality = 100
        self.max_reality = 100
        
        # Skills (Base levels)
        self.skills = {skill: 1 for skill in SkillSystem.SKILLS} # Start at 1
        
        # Systems
        self.thought_cabinet = ThoughtCabinet()
        self.flags = {}
        self.inventory = []
        self.history = [] # List of scene IDs visited
        self.injuries = [] # List of {name, healing_time_remaining, severity}
        
    def add_injury(self, name, healing_hours):
        self.injuries.append({
            "name": name,
            "healing_time_remaining": healing_hours * 60,
            "severity": 1
        })

    def modify_sanity(self, amount):
        old = self.sanity
        self.sanity = max(0, min(self.max_sanity, self.sanity + amount))
        return self.sanity - old

    def modify_reality(self, amount):
        old = self.reality
        self.reality = max(0, min(self.max_reality, self.reality + amount))
        return self.reality - old

    def get_skill_total(self, skill_name):
        base = self.skills.get(skill_name, 0)
        mods = self.thought_cabinet.get_modifiers()
        return base + mods.get(skill_name, 0)

    def update(self, minutes_passed=0):
        # Update thoughts (convert to seconds for legacy thought cabinet if needed, or update thought cabinet to minutes)
        # Assuming ThoughtCabinet uses seconds, 
        completed_thoughts = self.thought_cabinet.process_time(minutes_passed * 60)
        
        # Process Injuries
        healed = []
        for injury in self.injuries:
            injury["healing_time_remaining"] -= minutes_passed
            if injury["healing_time_remaining"] <= 0:
                healed.append(injury)
        
        for h in healed:
            self.injuries.remove(h)
            
        # Recalculate max stats based on thoughts
        mods = self.thought_cabinet.get_modifiers()
        
        # Base max is 100, apply modifiers
        new_max_sanity = 100 + mods.get("Sanity_Max", 0)
        new_max_reality = 100 + mods.get("Reality_Max", 0)
        
        self.max_sanity = new_max_sanity
        self.max_reality = new_max_reality
        
        # Clamp current values if max dropped
        self.sanity = min(self.sanity, self.max_sanity)
        self.reality = min(self.reality, self.max_reality)
        
        return completed_thoughts, healed
