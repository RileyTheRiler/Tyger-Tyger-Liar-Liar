"""
Config Loader - Loads and validates game configuration.
Provides centralized access to game settings and thresholds.
"""

import json
import os
from typing import Any, Dict, Optional


class GameConfig:
    """
    Singleton-style configuration loader.
    Loads game.config.json and provides typed access to settings.
    """

    _instance: Optional['GameConfig'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self, config_path: str = None):
        if self._loaded:
            return

        if config_path is None:
            # Try common locations
            possible_paths = [
                "game.config.json",
                os.path.join(os.path.dirname(__file__), "..", "game.config.json"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break

        if config_path and os.path.exists(config_path):
            self.load(config_path)
        else:
            print("[CONFIG] No config file found, using defaults")
            self._config = self._get_defaults()
            self._loaded = True

    def load(self, config_path: str):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self._loaded = True
            print(f"[CONFIG] Loaded from {config_path}")
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}")
            self._config = self._get_defaults()
            self._loaded = True

    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "game": {
                "starting_scene": "scene_arrival",
                "debug_mode_default": False
            },
            "player": {
                "starting_sanity": 100,
                "starting_reality": 100,
                "max_sanity": 100,
                "max_reality": 100
            },
            "population": {
                "starting_population": 347,
                "canonical_population": 347
            },
            "attention": {
                "starting_level": 0,
                "max_level": 100,
                "decay_rate_per_hour": 2.5
            },
            "dice": {
                "critical_success": 12,
                "critical_failure": 2,
                "partial_success_enabled": True
            }
        }

    def get(self, *keys, default=None) -> Any:
        """
        Get a nested configuration value using dot notation or key sequence.

        Example:
            config.get("player", "starting_sanity")
            config.get("dice", "difficulty_classes", "standard")
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self._config.get(section, {})

    # === Typed accessors for common settings ===

    @property
    def starting_scene(self) -> str:
        return self.get("game", "starting_scene", default="scene_arrival")

    @property
    def starting_sanity(self) -> int:
        return self.get("player", "starting_sanity", default=100)

    @property
    def starting_reality(self) -> int:
        return self.get("player", "starting_reality", default=100)

    @property
    def max_sanity(self) -> int:
        return self.get("player", "max_sanity", default=100)

    @property
    def max_reality(self) -> int:
        return self.get("player", "max_reality", default=100)

    @property
    def canonical_population(self) -> int:
        return self.get("population", "canonical_population", default=347)

    @property
    def attention_decay_rate(self) -> float:
        return self.get("attention", "decay_rate_per_hour", default=2.5)

    @property
    def believer_threshold(self) -> int:
        return self.get("lens", "believer_threshold", default=70)

    @property
    def skeptic_threshold(self) -> int:
        return self.get("lens", "skeptic_threshold", default=70)

    @property
    def haunted_threshold_attention(self) -> int:
        return self.get("lens", "haunted_threshold_attention", default=60)

    @property
    def haunted_threshold_sanity(self) -> int:
        return self.get("lens", "haunted_threshold_sanity", default=40)

    @property
    def partial_success_enabled(self) -> bool:
        return self.get("dice", "partial_success_enabled", default=True)

    @property
    def critical_success(self) -> int:
        return self.get("dice", "critical_success", default=12)

    @property
    def critical_failure(self) -> int:
        return self.get("dice", "critical_failure", default=2)

    def get_dc(self, difficulty: str) -> int:
        """Get difficulty class value by name."""
        dcs = self.get("dice", "difficulty_classes", default={})
        return dcs.get(difficulty.lower(), 9)  # Default to standard

    def get_path(self, path_name: str) -> str:
        """Get a configured path."""
        paths = self.get_section("paths")
        return paths.get(path_name, path_name)

    def get_attention_threshold(self, stage: str) -> int:
        """Get attention threshold for a stage name."""
        thresholds = self.get("attention", "thresholds", default={})
        return thresholds.get(stage.lower(), 0)

    def get_population_threshold_event(self, population: int) -> Optional[str]:
        """Get event flag for a population threshold."""
        thresholds = self.get("population", "thresholds", default={})
        # Find the highest threshold that matches
        matching_event = None
        for threshold_str, event in thresholds.items():
            try:
                threshold = int(threshold_str)
                if population <= threshold:
                    matching_event = event
            except ValueError:
                continue
        return matching_event

    def validate(self) -> Dict[str, list]:
        """
        Validate configuration values.
        Returns dict with 'errors' and 'warnings' lists.
        """
        errors = []
        warnings = []

        # Check required sections
        required_sections = ["game", "player", "population", "attention", "dice"]
        for section in required_sections:
            if section not in self._config:
                errors.append(f"Missing required section: {section}")

        # Validate numeric ranges
        sanity = self.starting_sanity
        if not 0 <= sanity <= 100:
            warnings.append(f"starting_sanity {sanity} outside typical range [0-100]")

        population = self.canonical_population
        if population != 347:
            warnings.append(f"canonical_population is {population}, not 347")

        # Validate thresholds
        if self.believer_threshold + self.skeptic_threshold > 140:
            warnings.append("Believer + Skeptic thresholds may make both impossible")

        return {"errors": errors, "warnings": warnings}

    def __repr__(self) -> str:
        return f"<GameConfig loaded={self._loaded} sections={list(self._config.keys())}>"


# Global singleton instance
_config: Optional[GameConfig] = None


def get_config(config_path: str = None) -> GameConfig:
    """Get or create the global GameConfig instance."""
    global _config
    if _config is None:
        _config = GameConfig(config_path)
    return _config


if __name__ == "__main__":
    # Test config loading
    config = get_config()
    print(f"Config: {config}")
    print(f"Starting scene: {config.starting_scene}")
    print(f"Starting sanity: {config.starting_sanity}")
    print(f"Population: {config.canonical_population}")
    print(f"Standard DC: {config.get_dc('standard')}")
    print(f"Hard DC: {config.get_dc('hard')}")

    # Validate
    validation = config.validate()
    if validation["errors"]:
        print(f"Errors: {validation['errors']}")
    if validation["warnings"]:
        print(f"Warnings: {validation['warnings']}")
