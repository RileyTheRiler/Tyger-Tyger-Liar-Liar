import json
import os
import hashlib
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
    """Manages game save/load functionality with hash verification."""
    
    def __init__(self, save_directory: str = "saves", export_directory: str = "exports"):
        self.save_directory = save_directory
        self.export_directory = export_directory
        
        # Create directories if they don't exist
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        if not os.path.exists(export_directory):
            os.makedirs(export_directory)
    
    def _validate_slot_id(self, slot_id: str) -> None:
        """Validate that the slot_id is safe to use as a filename."""
        # Allow alphanumeric, underscore, hyphen, and space
        # This prevents path traversal characters like / \ ..
        import re
        if not re.match(r'^[a-zA-Z0-9 _-]+$', slot_id):
            raise ValueError(f"Invalid save slot ID: '{slot_id}'. Only alphanumeric characters, spaces, underscores, and hyphens are allowed.")

    def _get_save_path(self, slot_id: str) -> str:
        """Get the full path for a save file."""
        self._validate_slot_id(slot_id)
        return os.path.join(self.save_directory, f"{slot_id}.json")
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of the save data (excluding the hash field itself)."""
        # Create a copy to avoid modifying the original
        data_to_hash = data.copy()
        if "hash" in data_to_hash:
            del data_to_hash["hash"]

        # Sort keys to ensure consistent JSON serialization
        # Use default=str to handle non-serializable objects like sets in hash calculation
        json_str = json.dumps(data_to_hash, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def save_game(self, slot_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Save game state to a file with hash verification.
        
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
                "version": "1.1",
                **state_data
            }
            
            # Calculate and append hash
            save_data["hash"] = self._calculate_hash(save_data)

            # Write to file with pretty formatting
            # Helper to handle non-serializable objects (like Enum)
            def default_serializer(obj):
                if hasattr(obj, 'value'): # Enum
                    return obj.value
                if hasattr(obj, 'to_dict'):
                    return obj.to_dict()
                if isinstance(obj, set):
                    return list(obj)
                raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=default_serializer)
            
            print(f"[SAVE] Game saved to slot '{slot_id}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save game: {e}")
            return False
    
    def load_game(self, slot_id: str) -> Optional[Dict[str, Any]]:
        """
        Load game state from a file and verify integrity.
        
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
            
            # Verify Hash if present
            stored_hash = save_data.get("hash")
            if stored_hash:
                calculated_hash = self._calculate_hash(save_data)
                if stored_hash != calculated_hash:
                    print(f"[WARNING] Save file integrity check FAILED for '{slot_id}'!")
                    print("          The file may have been corrupted or modified externally.")
                    # We continue loading but warn the user
                else:
                    print(f"[SYSTEM] Save integrity verified.")

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
                    
                    # Extract expanded metadata
                    saves.append({
                        "slot_id": slot_id,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "scene": data.get("scene", "Unknown"),
                        "summary": data.get("summary", "No summary"),
                        "datetime": data.get("datetime", "Unknown"),
                        "sanity": data.get("character_state", {}).get("player_state", {}).get("sanity", "??"),
                        "attention": data.get("additional_systems", {}).get("attention_system", {}).get("attention_level", "??"),
                        "active_theories": data.get("board_state", {}).get("active_count", 0) # Assuming this is available or derived
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
    
    def export_save(self, slot_id: str, filename: str) -> bool:
        """
        Export a save file to the exports directory.
        
        Args:
            slot_id: Save slot to export
            filename: Name of the export file (must be a safe filename, no paths)
        
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Validate filename (no path separators allowed)
            if filename != os.path.basename(filename):
                raise ValueError("Filename must not contain path separators.")

            # Validate characters (whitelist)
            import re
            if not re.match(r'^[a-zA-Z0-9 _\-\.]+$', filename):
                raise ValueError("Invalid filename. Only alphanumeric, spaces, underscores, hyphens, and dots allowed.")

            # Ensure strict pathing
            safe_path = os.path.join(self.export_directory, filename)

            # Canonicalize path to prevent any trickery (though regex covers most)
            if not os.path.abspath(safe_path).startswith(os.path.abspath(self.export_directory)):
                 raise ValueError("Path traversal attempted.")

            save_data = self.load_game(slot_id)
            if not save_data:
                return False
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"[EXPORT] Save exported to '{safe_path}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to export save: {e}")
            return False
