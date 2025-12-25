import random
from typing import Dict, List, Optional

class AmbientSystem:
    def __init__(self, weather_system, player_state, attention_system=None):
        self.weather_system = weather_system
        self.player_state = player_state
        self.attention_system = attention_system

        self.loops = {
            "wind": [
                "The tower creaks under the weight of wind.",
                "A loose sheet of metal bangs rhythmically against the wall.",
                "The wind howls like a wounded animal."
            ],
            "quiet": [
                "Somewhere, a single wind chime stirs, though you see no home.",
                "The silence is heavy, pressing against your ears.",
                "Snow crunches softly as it settles."
            ],
            "machinery": [
                "A low hum rises when you pass the radio array.",
                "Distant generators thrum beneath the ice.",
                "Clicking sounds echo from the ventilation."
            ]
        }

    def get_ambient_loop(self, location_tags: List[str] = []) -> str:
        """
        Get a passive ambient description based on weather and location.
        """
        weather = self.weather_system.get_current_condition()

        pool = []

        # Weather based
        if weather.name == "High Winds" or weather.name == "Whiteout":
            pool.extend(self.loops["wind"])
        elif weather.name == "Clear" or weather.name == "Overcast":
             pool.extend(self.loops["quiet"])

        # Location based (mock)
        if "industrial" in location_tags:
            pool.extend(self.loops["machinery"])

        if not pool:
            pool.extend(self.loops["quiet"])

        return random.choice(pool)

    def get_sensory_response(self, sense_type: str, location_tags: List[str] = []) -> str:
        """
        Handle 'listen', 'sniff', 'feel' commands.
        """
        weather = self.weather_system.get_current_condition()

        if sense_type == "listen":
            if weather.audio_mod < -10:
                return "The wind drowns out everything but the blood rushing in your ears."
            if "industrial" in location_tags:
                return "You hear the steady thrum of machinery and the tick of cooling metal."
            return "You hear the vast, empty silence of the tundra."

        elif sense_type == "sniff":
            if "industrial" in location_tags:
                return "The air smells of diesel and old rust."
            return "The air is sharp and metallic in your nose. It smells like snow."

        elif sense_type == "feel":
             wc = self.weather_system.calculate_wind_chill()
             if wc < -20:
                 return "The cold burns exposed skin instantly. You can feel the heat leaching from your body."
             return "You feel the vibration of the ground, a subtle trembling."

        return "You sense nothing unusual."

    def check_reactive_cues(self) -> Optional[str]:
        """
        Check for involuntary sensory cues based on stats.
        """
        # Sanity Hallucinations
        if self.player_state["sanity"] < 40:
             if random.random() < 0.1:
                 return "You hear a whistle that mimics your own—one you never made."

        # Attention High
        if self.attention_system and self.attention_system.attention_level > 40:
             if random.random() < 0.15:
                 return "A low hum rises when you pass the radio array."

        return None
