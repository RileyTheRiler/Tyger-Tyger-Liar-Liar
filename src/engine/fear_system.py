"""
Fear Event System - Week 15
Declarative fear event framework with trigger conditions and effects.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FearEvent:
    """Represents a single fear event with triggers and effects."""
    
    def __init__(self, data: dict):
        """
        Initialize a fear event from JSON data.
        
        Args:
            data: Dict containing event definition
        """
        self.id = data.get("id", "unknown_fear")
        self.name = data.get("name", "Unknown Fear")
        self.description = data.get("description", "")
        self.trigger_conditions = data.get("trigger_conditions", {})
        self.effects = data.get("effects", {})
        self.cooldown_minutes = data.get("cooldown_minutes", 30)
        self.last_triggered = None
    
    def can_trigger(self, game_state: dict) -> bool:
        """
        Check if this fear event's conditions are met.
        
        Args:
            game_state: Current game state dict
            
        Returns:
            True if event can trigger
        """
        # Check cooldown
        if self.last_triggered:
            time_since = (datetime.now() - self.last_triggered).total_seconds() / 60
            if time_since < self.cooldown_minutes:
                return False
        
        conditions = self.trigger_conditions
        
        # Location check
        if "location" in conditions:
            current_loc = game_state.get("current_location", "")
            required_locs = conditions["location"]
            if isinstance(required_locs, str):
                required_locs = [required_locs]
            if current_loc not in required_locs:
                return False
        
        # Location type check (e.g., "outdoor")
        if "location_type" in conditions:
            loc_data = game_state.get("location_data", {})
            loc_type = loc_data.get("type", "")
            if loc_type != conditions["location_type"]:
                return False
        
        # Player flags check
        if "flags" in conditions:
            player_flags = game_state.get("player_flags", set())
            required_flags = conditions["flags"]
            if isinstance(required_flags, str):
                required_flags = [required_flags]
            if not all(flag in player_flags for flag in required_flags):
                return False
        
        # Attention level check
        if "attention_above" in conditions:
            attention = game_state.get("attention_level", 0)
            if attention <= conditions["attention_above"]:
                return False
        
        if "attention_below" in conditions:
            attention = game_state.get("attention_level", 0)
            if attention >= conditions["attention_below"]:
                return False
        
        # Sanity check
        if "sanity_below" in conditions:
            sanity = game_state.get("sanity", 100)
            if sanity >= conditions["sanity_below"]:
                return False
        
        if "sanity_above" in conditions:
            sanity = game_state.get("sanity", 100)
            if sanity <= conditions["sanity_above"]:
                return False
        
        # Time of day check
        if "time_of_day" in conditions:
            current_time = game_state.get("time", None)
            required_time = conditions["time_of_day"]
            if current_time:
                hour = current_time.hour
                if required_time == "night" and not (20 <= hour or hour < 6):
                    return False
                elif required_time == "day" and not (6 <= hour < 20):
                    return False
        
        # Weather check
        if "weather" in conditions:
            current_weather = game_state.get("current_weather", "")
            required_weather = conditions["weather"]
            if isinstance(required_weather, str):
                required_weather = [required_weather]
            if current_weather not in required_weather:
                return False
        
        # Random chance (if specified)
        if "chance" in conditions:
            import random
            if random.random() > conditions["chance"]:
                return False
        
        return True
    
    def trigger(self) -> Dict:
        """
        Mark event as triggered and return effects.
        
        Returns:
            Dict containing effects to apply
        """
        self.last_triggered = datetime.now()
        return self.effects.copy()


class FearManager:
    """Manages fear events and their triggering."""
    
    def __init__(self):
        """Initialize the fear manager."""
        self.fear_events: Dict[str, FearEvent] = {}
        self.enabled = True  # Can be toggled for debugging
    
    def load_fear_events(self, directory_path: str):
        """
        Load fear events from a directory of JSON files.
        
        Args:
            directory_path: Path to directory containing fear event JSON files
        """
        if not os.path.exists(directory_path):
            print(f"[FearManager] Warning: Fear events directory not found: {directory_path}")
            return
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                filepath = os.path.join(directory_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle both single event and array of events
                        if isinstance(data, list):
                            for event_data in data:
                                event = FearEvent(event_data)
                                self.fear_events[event.id] = event
                        else:
                            event = FearEvent(data)
                            self.fear_events[event.id] = event
                    
                    print(f"[FearManager] Loaded fear events from {filename}")
                except Exception as e:
                    print(f"[FearManager] Error loading {filename}: {e}")
    
    def load_fear_event_file(self, filepath: str):
        """
        Load a single fear event file.
        
        Args:
            filepath: Path to JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                event = FearEvent(data)
                self.fear_events[event.id] = event
                print(f"[FearManager] Loaded fear event: {event.id}")
        except Exception as e:
            print(f"[FearManager] Error loading fear event from {filepath}: {e}")
    
    def check_fear_triggers(self, game_state: dict) -> List[Dict]:
        """
        Check all fear events and return those that should trigger.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of triggered event effects
        """
        if not self.enabled:
            return []
        
        triggered_events = []
        
        for event in self.fear_events.values():
            if event.can_trigger(game_state):
                effects = event.trigger()
                effects["event_id"] = event.id
                effects["event_name"] = event.name
                triggered_events.append(effects)
        
        return triggered_events
    
    def force_trigger_event(self, event_id: str) -> Optional[Dict]:
        """
        Force trigger a specific event (for debugging/testing).
        
        Args:
            event_id: ID of event to trigger
            
        Returns:
            Event effects or None if not found
        """
        event = self.fear_events.get(event_id)
        if event:
            return event.trigger()
        return None
    
    def reset_cooldowns(self):
        """Reset all event cooldowns (for debugging)."""
        for event in self.fear_events.values():
            event.last_triggered = None
    
    def toggle_enabled(self, enabled: bool = None) -> bool:
        """
        Toggle or set fear events enabled state.
        
        Args:
            enabled: If provided, set to this value. Otherwise toggle.
            
        Returns:
            New enabled state
        """
        if enabled is None:
            self.enabled = not self.enabled
        else:
            self.enabled = enabled
        
        return self.enabled
    
    def get_event_status(self, event_id: str) -> Optional[Dict]:
        """
        Get status information about a specific event.
        
        Args:
            event_id: Event to check
            
        Returns:
            Dict with event status or None
        """
        event = self.fear_events.get(event_id)
        if not event:
            return None
        
        status = {
            "id": event.id,
            "name": event.name,
            "cooldown_minutes": event.cooldown_minutes,
            "last_triggered": event.last_triggered.isoformat() if event.last_triggered else None
        }
        
        if event.last_triggered:
            time_since = (datetime.now() - event.last_triggered).total_seconds() / 60
            status["minutes_since_trigger"] = time_since
            status["can_trigger_again_in"] = max(0, event.cooldown_minutes - time_since)
        
        return status
    
    def get_all_events_status(self) -> List[Dict]:
        """Get status of all fear events."""
        return [self.get_event_status(event_id) for event_id in self.fear_events.keys()]
