import json
import time

class Thought:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.completion_text = data.get("completion_text", "Thought complete.")
        self.temporary_effects = data.get("temporary_effects", {})
        self.permanent_effects = data.get("permanent_effects", {})
        self.internalization_time = data.get("internalization_time_seconds", 60)
        
        # Runtime state
        self.progress = 0.0 # Seconds internalized
        self.is_internalized = False
        self.is_active = False # Currently in the "cabinet" processing

class ThoughtCabinet:
    def __init__(self):
        self.available_thoughts = {} # All thoughts in the game DB
        self.inventory = [] # Thoughts the player has discovered/unlocked (ids)
        self.active_thoughts = [] # Thoughts currently being internalized (Thought objects)
        self.internalized_thoughts = [] # Thoughts completed (Thought objects)
        self.max_slots = 3
    
    def load_thoughts(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data:
                    t = Thought(item)
                    self.available_thoughts[t.id] = t
        except Exception as e:
            print(f"Error loading thoughts: {e}")

    def unlock_thought(self, thought_id):
        if thought_id in self.available_thoughts and thought_id not in self.inventory:
            self.inventory.append(thought_id)
            return True
        return False

    def equip_thought(self, thought_id):
        if len(self.active_thoughts) >= self.max_slots:
            return False, "Cabinet full"
        
        if thought_id not in self.inventory:
             return False, "Thought not known"

        # Check if already processing or done
        for t in self.active_thoughts:
            if t.id == thought_id: return False, "Already internalizing"
        for t in self.internalized_thoughts:
            if t.id == thought_id: return False, "Already internalized"
            
        thought = self.available_thoughts[thought_id]
        thought.is_active = True
        self.active_thoughts.append(thought)
        return True, "Thought equipped"

    def process_time(self, seconds):
        completed = []
        for thought in self.active_thoughts:
            thought.progress += seconds
            if thought.progress >= thought.internalization_time:
                thought.is_internalized = True
                thought.is_active = False
                self.internalized_thoughts.append(thought)
                completed.append(thought)
        
        # Remove completed from active
        self.active_thoughts = [t for t in self.active_thoughts if not t.is_internalized]
        return completed

    def get_modifiers(self):
        mods = {}
        
        # Apply temporary effects from active thoughts
        for t in self.active_thoughts:
            for stat, val in t.temporary_effects.items():
                mods[stat] = mods.get(stat, 0) + val
                
        # Apply permanent effects from internalized thoughts
        for t in self.internalized_thoughts:
            for stat, val in t.permanent_effects.items():
                mods[stat] = mods.get(stat, 0) + val
        
        return mods
