import random
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class WeatherCondition:
    name: str
    description: str
    visibility_mod: int  # Modifier for Perception checks
    audio_mod: int       # Modifier for listening/hearing
    travel_mod: float    # Multiplier for travel time
    stamina_drain: int   # Constitution check DC modifier or damage?
    stealth_mod: int     # Modifier for Stealth checks
    integration_mask: bool # If True, masks thermal drift

class WeatherSystem:
    def __init__(self):
        self.conditions = {
            "clear": WeatherCondition("Clear", "The sky is open and cold.", 0, 0, 1.0, 0, -10, False),
            "overcast": WeatherCondition("Overcast", "A blanket of grey stifles the light.", -10, 5, 1.0, 0, 0, False),
            "snow": WeatherCondition("Light Snow", "Flakes drift lazily, softening edges.", -20, 10, 1.2, 5, 10, True),
            "wind": WeatherCondition("High Winds", "The wind howls, tearing at your clothes.", -10, -30, 1.5, 10, -20, True),
            "aurora": WeatherCondition("Aurora", "The sky burns with green and violet fire.", 0, 0, 1.0, 0, -20, False), # High visibility? Or distraction?
            "ice_fog": WeatherCondition("Ice Fog", "Crystals hang in the air, refracting light.", -40, 20, 1.5, 15, 20, True),
            "whiteout": WeatherCondition("Whiteout", "The world is gone. There is only white.", -80, -50, 3.0, 20, 40, True)
        }
        self.current_condition_key = "clear"
        self.temperature = -15 # Base temp
        self.wind_speed = 5 # mph
        self.next_shift_time = 0 # minutes until next shift

    def get_current_condition(self) -> WeatherCondition:
        return self.conditions.get(self.current_condition_key, self.conditions["clear"])

    def update(self, minutes_passed: int, attention_level: int = 0):
        self.next_shift_time -= minutes_passed
        if self.next_shift_time <= 0:
            self._shift_weather(attention_level=attention_level)

    def _shift_weather(self, force_condition: Optional[str] = None, attention_level: int = 0):
        if force_condition and force_condition in self.conditions:
            self.current_condition_key = force_condition
        else:
            # Logic for shifting based on current state
            options = ["clear", "overcast", "snow", "wind", "aurora", "ice_fog", "whiteout"]

            # Base weights
            weights = [30, 25, 20, 15, 5, 4, 1]

            # Dynamic adjustment based on Attention (Entity presence)
            # Aurora index is 4
            if attention_level > 50:
                weights[4] += int((attention_level - 50) * 1.5) # Boost Aurora significantly

            self.current_condition_key = random.choices(options, weights=weights, k=1)[0]

        # Reset timer (6-12 hours)
        self.next_shift_time = random.randint(6, 12) * 60

        # Update temps
        base = -20
        variation = random.randint(-15, 15)
        self.temperature = base + variation

        # Update wind
        if self.current_condition_key in ["wind", "whiteout"]:
            self.wind_speed = random.randint(30, 60)
        elif self.current_condition_key == "clear":
             self.wind_speed = random.randint(0, 10)
        else:
             self.wind_speed = random.randint(5, 25)

    def calculate_wind_chill(self) -> int:
        # T(wc) = 35.74 + 0.6215T - 35.75(V^0.16) + 0.4275T(V^0.16)
        T = self.temperature
        V = self.wind_speed
        if V < 3: return int(T)
        wc = 35.74 + 0.6215 * T - 35.75 * (V**0.16) + 0.4275 * T * (V**0.16)
        return int(wc)

    def get_status_string(self) -> str:
        wc = self.calculate_wind_chill()
        cond = self.get_current_condition()

        vis_mod = cond.visibility_mod
        if vis_mod <= -50: vis_str = "Zero"
        elif vis_mod <= -30: vis_str = "Poor"
        elif vis_mod < 0: vis_str = "Reduced"
        else: vis_str = "Good"

        return f"~ {cond.name}. Temp: {self.temperature}°F (Feels like {wc}°F). Visibility: {vis_str} ~"

    def get_flavor_text(self) -> str:
        # TODO: Load from data file or dict
        return self.get_current_condition().description

    def to_dict(self):
        return {
            "current_condition": self.current_condition_key,
            "temperature": self.temperature,
            "wind_speed": self.wind_speed,
            "next_shift_time": self.next_shift_time
        }

    def from_dict(self, data):
        self.current_condition_key = data.get("current_condition", "clear")
        self.temperature = data.get("temperature", -15)
        self.wind_speed = data.get("wind_speed", 5)
        self.next_shift_time = data.get("next_shift_time", 0)
