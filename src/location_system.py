import json
import os

class LocationManager:
    def __init__(self):
        self.locations = {}
        # location_states will be stored in player_state in game.py
        # but handled through this manager
        
    def load_locations(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.locations = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading locations from {filepath}: {e}")
            return False

    def get_location(self, location_id):
        return self.locations.get(location_id)

    def get_connected_locations(self, location_id):
        loc = self.get_location(location_id)
        if loc:
            return loc.get("connected_to", {})
        return {}

    def can_enter(self, location_id, game_state):
        loc = self.get_location(location_id)
        if not loc:
            return False
            
        conditions = loc.get("enter_conditions", {})
        
        # Check Flags Required
        req_flags = conditions.get("flags_required", [])
        for flag in req_flags:
            if flag not in game_state.get("player_flags", set()):
                return False
                
        # Check Flags Forbidden
        forb_flags = conditions.get("flags_forbidden", [])
        for flag in forb_flags:
            if flag in game_state.get("player_flags", set()):
                return False
            # Also check location state flags if applicable
            loc_state = game_state.get("location_states", {}).get(location_id, {})
            if loc_state.get(flag):
                return False

        # Check Locked State
        loc_state = game_state.get("location_states", {}).get(location_id, {})
        if loc_state.get("locked"):
            # For now, if it's locked, you can't enter unless you have a key or something?
            # We'll treat 'locked' as a hard block unless handled elsewhere
            return False

        # Check Time Range
        time_range = conditions.get("time_range")
        if time_range:
            start_h, end_h = time_range
            current_h = game_state.get("time").hour
            if start_h <= end_h:
                if not (start_h <= current_h < end_h):
                    return False
            else: # Overnight
                if not (current_h >= start_h or current_h < end_h):
                    return False

        return True

    def get_location_flag(self, location_id, flag, game_state):
        return game_state.get("location_states", {}).get(location_id, {}).get(flag, False)

    def initialize_states(self):
        """Returns initial state dictionary for all locations."""
        states = {}
        for loc_id, data in self.locations.items():
            states[loc_id] = data.get("state", {}).copy()
        return states
