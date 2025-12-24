import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class EventLog:
    """Manages a log of significant game events."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    
    def add_event(self, event_type: str, **details):
        """
        Add an event to the log.
        
        Args:
            event_type: Type of event (e.g., "scene_entry", "skill_check", "combat", "theory")
            **details: Keyword arguments containing event-specific data
        """
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            **details
        }
        self.events.append(event)
    
    def get_logs(self, event_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve event logs, optionally filtered by type.
        
        Args:
            event_type: If provided, only return events of this type
            limit: If provided, only return the last N events
        """
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]
        
        if limit:
            filtered = filtered[-limit:]
        
        return filtered
    
    def to_dict(self) -> dict:
        """Serialize event log to dictionary."""
        return {"events": self.events}
    
    @staticmethod
    def from_dict(data: dict) -> 'EventLog':
        """Deserialize event log from dictionary."""
        log = EventLog()
        log.events = data.get("events", [])
        return log


class SaveSystem:
    """Manages game save/load functionality."""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        
        # Create saves directory if it doesn't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
    
    def _get_save_path(self, slot_id: str) -> str:
        """Get the full path for a save file."""
        return os.path.join(self.save_directory, f"{slot_id}.json")
    
    def save_game(self, slot_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Save game state to a file.
        
        Args:
            slot_id: Unique identifier for this save slot
            state_data: Dictionary containing all game state
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(slot_id)
            
            # Add metadata
            save_data = {
                "id": slot_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",  # For future compatibility
                **state_data
            }
            
            # Write to file with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"[SAVE] Game saved to slot '{slot_id}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save game: {e}")
            return False
    
    def load_game(self, slot_id: str) -> Optional[Dict[str, Any]]:
        """
        Load game state from a file.
        
        Args:
            slot_id: Unique identifier for the save slot to load
        
        Returns:
            Dictionary containing game state, or None if load failed
        """
        try:
            save_path = self._get_save_path(slot_id)
            
            if not os.path.exists(save_path):
                print(f"[ERROR] Save file '{slot_id}' not found")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            print(f"[LOAD] Game loaded from slot '{slot_id}'")
            return save_data
            
        except Exception as e:
            print(f"[ERROR] Failed to load game: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, str]]:
        """
        List all available save files with metadata.
        
        Returns:
            List of dictionaries containing save metadata
        """
        saves = []
        
        if not os.path.exists(self.save_directory):
            return saves
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                slot_id = filename[:-5]  # Remove .json extension
                save_path = self._get_save_path(slot_id)
                
                try:
                    with open(save_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    saves.append({
                        "slot_id": slot_id,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "scene": data.get("scene", "Unknown"),
                        "summary": data.get("summary", "No summary"),
                        "datetime": data.get("datetime", "Unknown")
                    })
                except Exception as e:
                    print(f"[WARNING] Could not read save file '{filename}': {e}")
        
        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x["timestamp"], reverse=True)
        return saves
    
    def delete_save(self, slot_id: str) -> bool:
        """
        Delete a save file.
        
        Args:
            slot_id: Unique identifier for the save slot to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(slot_id)
            
            if not os.path.exists(save_path):
                print(f"[ERROR] Save file '{slot_id}' not found")
                return False
            
            os.remove(save_path)
            print(f"[DELETE] Save '{slot_id}' deleted")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to delete save: {e}")
            return False
    
    def export_save(self, slot_id: str, output_path: str) -> bool:
        """
        Export a save file to a different location (for backup/sharing).
        
        Args:
            slot_id: Save slot to export
            output_path: Destination file path
        
        Returns:
            True if export was successful, False otherwise
        """
        try:
            save_data = self.load_game(slot_id)
            if not save_data:
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"[EXPORT] Save exported to '{output_path}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to export save: {e}")
            return False
