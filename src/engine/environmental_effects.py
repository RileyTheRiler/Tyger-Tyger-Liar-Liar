"""
Environmental Effects System - Weather, lighting, and terrain modifiers.

Provides dynamic environmental conditions that affect skill checks and gameplay.
"""

from typing import Dict, List, Optional
import random


class EnvironmentalEffects:
    """Manages environmental conditions and their gameplay effects."""
    
    # Weather effect definitions
    WEATHER_EFFECTS = {
        "clear": {},
        "rain": {
            "Perception": -1,
            "Reflexes": -1,
            "Firearms": -1,
            "description": "Rain obscures vision and makes surfaces slippery."
        },
        "heavy_rain": {
            "Perception": -2,
            "Reflexes": -2,
            "Firearms": -2,
            "Stealth": 1,
            "description": "Heavy rain severely limits visibility and movement."
        },
        "fog": {
            "Perception": -2,
            "Firearms": -2,
            "Stealth": 2,
            "description": "Thick fog blankets the area, reducing visibility to mere feet."
        },
        "snow": {
            "Athletics": -1,
            "Reflexes": -1,
            "Perception": -1,
            "description": "Snow covers the ground, making movement difficult."
        },
        "blizzard": {
            "Perception": -3,
            "Athletics": -2,
            "Reflexes": -2,
            "Endurance": -1,
            "description": "A fierce blizzard rages, making survival itself a challenge."
        },
        "ice": {
            "Reflexes": -2,
            "Athletics": -2,
            "description": "Ice covers every surface. One wrong step could be fatal."
        },
        "wind": {
            "Perception": -1,
            "Firearms": -2,
            "description": "Strong winds buffet you, making ranged attacks difficult."
        }
    }
    
    # Lighting effect definitions
    LIGHTING_EFFECTS = {
        "bright": {},
        "normal": {},
        "dim": {
            "Perception": -1,
            "Firearms": -1,
            "description": "Dim lighting makes it hard to see details."
        },
        "dark": {
            "Perception": -2,
            "Firearms": -2,
            "Reflexes": -1,
            "Stealth": 2,
            "description": "Darkness shrouds everything. You can barely see."
        },
        "pitch_black": {
            "Perception": -4,
            "Firearms": -4,
            "Reflexes": -2,
            "Stealth": 3,
            "description": "Total darkness. You cannot see your hand in front of your face."
        },
        "blinding": {
            "Perception": -3,
            "Reflexes": -2,
            "description": "Harsh light blinds you temporarily."
        }
    }
    
    # Terrain effect definitions
    TERRAIN_EFFECTS = {
        "normal": {},
        "mud": {
            "Athletics": -1,
            "Stealth": -1,
            "Reflexes": -1,
            "description": "Thick mud clings to your boots."
        },
        "rubble": {
            "Athletics": -2,
            "Reflexes": -1,
            "description": "Broken rubble makes every step treacherous."
        },
        "water_shallow": {
            "Athletics": -1,
            "Stealth": -2,
            "description": "You wade through shallow water."
        },
        "water_deep": {
            "Athletics": -2,
            "Reflexes": -2,
            "Endurance": -1,
            "description": "Deep water slows your movement significantly."
        },
        "dense_vegetation": {
            "Athletics": -1,
            "Perception": -1,
            "Stealth": 1,
            "description": "Thick vegetation impedes movement but provides cover."
        },
        "steep_incline": {
            "Athletics": -2,
            "description": "The steep slope makes climbing difficult."
        }
    }
    
    def __init__(self):
        self.current_weather = "clear"
        self.current_lighting = "normal"
        self.current_terrain = "normal"
        self.active_modifiers: Dict[str, int] = {}
        
    def set_weather(self, weather: str):
        """Set current weather condition."""
        if weather in self.WEATHER_EFFECTS:
            self.current_weather = weather
            self._recalculate_modifiers()
        else:
            print(f"[EnvironmentalEffects] Unknown weather: {weather}")
    
    def set_lighting(self, lighting: str):
        """Set current lighting condition."""
        if lighting in self.LIGHTING_EFFECTS:
            self.current_lighting = lighting
            self._recalculate_modifiers()
        else:
            print(f"[EnvironmentalEffects] Unknown lighting: {lighting}")
    
    def set_terrain(self, terrain: str):
        """Set current terrain type."""
        if terrain in self.TERRAIN_EFFECTS:
            self.current_terrain = terrain
            self._recalculate_modifiers()
        else:
            print(f"[EnvironmentalEffects] Unknown terrain: {terrain}")
    
    def _recalculate_modifiers(self):
        """Recalculate total modifiers from all environmental factors."""
        self.active_modifiers = {}
        
        # Combine all effects
        for effect_dict in [
            self.WEATHER_EFFECTS.get(self.current_weather, {}),
            self.LIGHTING_EFFECTS.get(self.current_lighting, {}),
            self.TERRAIN_EFFECTS.get(self.current_terrain, {})
        ]:
            for skill, modifier in effect_dict.items():
                if skill != "description":
                    self.active_modifiers[skill] = self.active_modifiers.get(skill, 0) + modifier
    
    def get_modifier(self, skill_name: str) -> int:
        """Get total environmental modifier for a skill."""
        return self.active_modifiers.get(skill_name, 0)
    
    def get_all_modifiers(self) -> Dict[str, int]:
        """Get all active environmental modifiers."""
        return self.active_modifiers.copy()
    
    def get_description(self) -> str:
        """Get narrative description of current environmental conditions."""
        descriptions = []
        
        weather_desc = self.WEATHER_EFFECTS.get(self.current_weather, {}).get("description")
        if weather_desc:
            descriptions.append(weather_desc)
        
        lighting_desc = self.LIGHTING_EFFECTS.get(self.current_lighting, {}).get("description")
        if lighting_desc:
            descriptions.append(lighting_desc)
        
        terrain_desc = self.TERRAIN_EFFECTS.get(self.current_terrain, {}).get("description")
        if terrain_desc:
            descriptions.append(terrain_desc)
        
        return " ".join(descriptions) if descriptions else "Conditions are normal."
    
    def apply_to_skill_system(self, skill_system):
        """Apply environmental modifiers to skill system."""
        # Clear old environmental modifiers
        for skill in skill_system.skills.values():
            skill.set_modifier("Environment", 0)
        
        # Apply new modifiers
        for skill_name, modifier in self.active_modifiers.items():
            skill = skill_system.get_skill(skill_name)
            if skill:
                skill.set_modifier("Environment", modifier)
    
    def random_weather_change(self) -> Optional[str]:
        """Randomly change weather (for dynamic world)."""
        # Simple weather progression
        transitions = {
            "clear": ["clear", "clear", "rain", "fog"],
            "rain": ["rain", "heavy_rain", "clear", "fog"],
            "heavy_rain": ["rain", "heavy_rain", "clear"],
            "fog": ["fog", "clear", "rain"],
            "snow": ["snow", "blizzard", "clear"],
            "blizzard": ["snow", "blizzard"],
            "ice": ["ice", "snow"],
            "wind": ["wind", "clear", "rain"]
        }
        
        possible = transitions.get(self.current_weather, ["clear"])
        new_weather = random.choice(possible)
        
        if new_weather != self.current_weather:
            self.set_weather(new_weather)
            return f"The weather changes: {self.WEATHER_EFFECTS[new_weather].get('description', '')}"
        
        return None
    
    def get_status(self) -> str:
        """Get formatted status of environmental conditions."""
        status = "=== ENVIRONMENTAL CONDITIONS ===\n"
        status += f"Weather: {self.current_weather.replace('_', ' ').title()}\n"
        status += f"Lighting: {self.current_lighting.replace('_', ' ').title()}\n"
        status += f"Terrain: {self.current_terrain.replace('_', ' ').title()}\n"
        
        if self.active_modifiers:
            status += "\nActive Modifiers:\n"
            for skill, mod in sorted(self.active_modifiers.items()):
                sign = "+" if mod > 0 else ""
                status += f"  {skill}: {sign}{mod}\n"
        
        status += f"\n{self.get_description()}\n"
        
        return status
    
    def to_dict(self) -> dict:
        """Serialize environmental state."""
        return {
            "weather": self.current_weather,
            "lighting": self.current_lighting,
            "terrain": self.current_terrain
        }
    
    def from_dict(self, data: dict):
        """Restore environmental state."""
        self.current_weather = data.get("weather", "clear")
        self.current_lighting = data.get("lighting", "normal")
        self.current_terrain = data.get("terrain", "normal")
        self._recalculate_modifiers()
