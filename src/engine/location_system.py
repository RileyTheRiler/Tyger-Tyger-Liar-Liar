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

    def find_location_by_name(self, name):
        """Find a location ID by name or partial name."""
        name = name.lower().strip()
        # Direct ID check
        if name in self.locations:
            return name
            
        # Name check
        for loc_id, data in self.locations.items():
            loc_name = data.get("name", "").lower()
            if name == loc_name:
                return loc_id
            if name in loc_name or loc_name in name:
                return loc_id
        return None

    def get_connected_locations(self, location_id):
        loc = self.get_location(location_id)
        if loc:
            return loc.get("connected_to", {})
        return {}

    def can_enter(self, location_id, game_state):
        """
        Check if player can enter location.
        Returns: (success: bool, reason: str)
        """
        loc = self.get_location(location_id)
        if not loc:
            return False, "Unknown location."
            
        conditions = loc.get("enter_conditions", {})
        
        # Check Flags Required
        req_flags = conditions.get("flags_required", [])
        for flag in req_flags:
            if flag not in game_state.get("player_flags", set()):
                return False, conditions.get("failure_msg", f"You are not ready to enter {loc['name']}.")
                
        # Check Flags Forbidden
        forb_flags = conditions.get("flags_forbidden", [])
        for flag in forb_flags:
            if flag in game_state.get("player_flags", set()):
                return False, conditions.get("failure_msg", f"Access to {loc['name']} is currently blocked.")
            # Also check location state flags if applicable
            loc_state = game_state.get("location_states", {}).get(location_id, {})
            if loc_state.get(flag):
                return False, conditions.get("failure_msg", f"Access to {loc['name']} is blocked.")

        # Check Locked State
        loc_state = game_state.get("location_states", {}).get(location_id, {})
        if loc_state.get("locked"):
            return False, f"The door to {loc['name']} is locked."

        # Check Time Range (Hours)
        time_range = conditions.get("time_range")
        if time_range:
            start_h, end_h = time_range
            current_h = game_state.get("time").hour

            # Helper to check if time is within range [start, end)
            in_range = False
            if start_h < end_h:
                in_range = (start_h <= current_h < end_h)
            else: # Overnight range (e.g. 22 to 06)
                in_range = (current_h >= start_h or current_h < end_h)

            if not in_range:
                msg = conditions.get("time_msg", f"This area is only accessible between {start_h:02d}:00 and {end_h:02d}:00.")
                return False, msg

        # Check Time Range (Restricted Hours - Blocked during this time)
        restricted_hours = conditions.get("restricted_hours")
        if restricted_hours:
            start_h, end_h = restricted_hours
            current_h = game_state.get("time").hour

            in_restricted = False
            if start_h < end_h:
                in_restricted = (start_h <= current_h < end_h)
            else:
                in_restricted = (current_h >= start_h or current_h < end_h)

            if in_restricted:
                msg = conditions.get("restricted_msg", f"It is not safe to enter {loc['name']} right now.")
                return False, msg

        # Check Days Passed
        min_days = conditions.get("min_days_passed")
        if min_days is not None:
            # We assume game_state has 'days_passed' from TimeSystem
            current_days = game_state.get("days_passed", 0)
            if current_days < min_days:
                return False, conditions.get("days_msg", f"This area is not yet accessible.")

        return True, "Access granted."

    def get_location_flag(self, location_id, flag, game_state):
        return game_state.get("location_states", {}).get(location_id, {}).get(flag, False)

    def initialize_states(self):
        """Returns initial state dictionary for all locations."""
        states = {}
        for loc_id, data in self.locations.items():
            states[loc_id] = data.get("state", {}).copy()
        return states
