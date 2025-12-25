import random
from typing import Dict, List, Optional, Any

class EnvironmentalSystem:
    def __init__(self, time_system, weather_system, player_state):
        self.time_system = time_system
        self.weather_system = weather_system
        self.player_state = player_state

        # Define triggers based on location type
        # In a real implementation, these might load from JSON
        self.location_triggers = {
            "dew_station": ["glitch", "memory_fragment", "aurora_interference"],
            "shrine": ["grounding_ritual"],
            "frozen_lake": ["reflection_anomaly"],
            "tower": ["audio_warp"]
        }

    def check_triggers(self, location_type: str) -> Optional[str]:
        """
        Check for environmental events based on current location type and conditions.
        Returns a descriptive string if an event occurs, else None.
        """
        if not location_type:
            return None

        possible_events = self.location_triggers.get(location_type, [])
        if not possible_events:
            return None

        # Chance to trigger event
        if random.random() < 0.2: # 20% chance per check (e.g. per turn or entry)
            event = random.choice(possible_events)
            return self.process_event(event)

        return None

    def process_event(self, event_key: str) -> str:
        if event_key == "glitch":
            return "The geometry of the ruins seems to shift when you blink."
        elif event_key == "memory_fragment":
            return "You hear a snippet of conversation, though no one is here."
        elif event_key == "aurora_interference":
            if self.weather_system.current_condition_key == "aurora":
                return "The radio crackles violently with the rhythm of the lights above."
            else:
                return "Static washes over your senses."
        elif event_key == "grounding_ritual":
            return "The shrine stands silent. The air here feels... stable. (You can PERFORM RITUAL here)"
        elif event_key == "reflection_anomaly":
            if self.player_state["sanity"] < 50:
                 return "Your reflection in the ice stares back, but it isn't moving."
            return "The ice is dark and deep."
        elif event_key == "audio_warp":
            return "The wind passing through the tower sounds like overlapping voices."

        return ""

    def perform_ritual(self, location_type: str) -> Dict[str, Any]:
        """
        Attempt to perform a ritual at the current location.
        """
        if location_type == "shrine":
            # Iñupiaq shrine logic
            self.player_state["sanity"] = min(100, self.player_state["sanity"] + 15)
            # Maybe reduce paranoia or corruption?
            return {"success": True, "message": "You breathe in the cold air and center yourself. The spirits are quiet here. (+15 Sanity)"}

        return {"success": False, "message": "This is not a place for rituals."}
