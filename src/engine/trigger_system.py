import json
from datetime import datetime

class TriggerManager:
    def __init__(self):
        self.triggers = []
        self.fired_triggers = set()

    def load_triggers(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.triggers = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading triggers from {filepath}: {e}")
            return False

    def check_triggers(self, game_state):
        triggered = []
        # Sort by priority descending
        active_triggers = sorted(self.triggers, key=lambda x: x.get("priority", 0), reverse=True)
        
        for trigger in active_triggers:
            if trigger["id"] in self.fired_triggers and trigger.get("once_only", True):
                continue
                
            if self.evaluate_conditions(trigger, game_state):
                triggered.append(trigger)
                if trigger.get("once_only", True):
                    self.fired_triggers.add(trigger["id"])
                    
        return triggered

    def evaluate_conditions(self, trigger, game_state):
        conditions = trigger.get("conditions", {})
        
        # Location
        if "location" in trigger:
            if game_state.get("current_location") != trigger["location"]:
                return False
                
        # Time After
        if "time_after" in conditions:
            time_after = datetime.strptime(conditions["time_after"], "%H:%M").time()
            current_time = game_state.get("time").time()
            if current_time < time_after:
                return False
                
        # Time Before
        if "time_before" in conditions:
            time_before = datetime.strptime(conditions["time_before"], "%H:%M").time()
            current_time = game_state.get("time").time()
            if current_time > time_before:
                return False

        # Location Flags
        loc_flags = conditions.get("location_flags", {})
        cur_loc = game_state.get("current_location")
        if loc_flags and cur_loc:
            loc_state = game_state.get("location_states", {}).get(cur_loc, {})
            for flag, val in loc_flags.items():
                if loc_state.get(flag) != val:
                    return False

        # Player Flags
        player_flags = conditions.get("player_flags", [])
        active_flags = game_state.get("player_flags", set())
        for flag in player_flags:
            if flag not in active_flags:
                return False

        # Theory Check
        if "has_theory" in conditions:
            theory_id = conditions["has_theory"]
            board = game_state.get("board")
            if board:
                theory = board.get_theory(theory_id)
                if not theory or theory.status != "active":
                    return False

        # Stats
        if "sanity_below" in conditions:
            if game_state.get("sanity", 100) >= conditions["sanity_below"]:
                return False
        
        if "reality_below" in conditions:
            if game_state.get("reality", 100) >= conditions["reality_below"]:
                return False

        return True

    def to_dict(self):
        return {
            "fired_triggers": list(self.fired_triggers)
        }

    def from_dict(self, data):
        self.fired_triggers = set(data.get("fired_triggers", []))
