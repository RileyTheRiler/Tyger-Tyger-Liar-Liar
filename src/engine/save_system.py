import json
import os
import gzip
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
    
    def _get_save_path(self, slot_id: str, compressed: bool = False) -> str:
        """Get the full path for a save file."""
        ext = ".dat" if compressed else ".json"
        # Check if user already provided extension in slot_id, though usually not expected
        if slot_id.endswith(".json") or slot_id.endswith(".dat"):
            return os.path.join(self.save_directory, slot_id)
        return os.path.join(self.save_directory, f"{slot_id}{ext}")
    
    def save_game(self, slot_id: str, state_data: Dict[str, Any], compress: bool = False) -> bool:
        """
        Save game state to a file.
        
        Args:
            slot_id: Unique identifier for this save slot
            state_data: Dictionary containing all game state
            compress: Whether to compress the save file (gzip)
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            save_path = self._get_save_path(slot_id, compressed=compress)
            
            # Add metadata
            save_data = {
                "id": slot_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",  # For future compatibility
                "compressed": compress,
                **state_data
            }
            
            if compress:
                with gzip.open(save_path, 'wt', encoding='utf-8') as f:
                    json.dump(save_data, f)
                # Cleanup potential duplicate uncompressed file
                alt_path = self._get_save_path(slot_id, compressed=False)
                if os.path.exists(alt_path) and alt_path != save_path:
                    os.remove(alt_path)
            else:
                # Write to file with pretty formatting
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                # Cleanup potential duplicate compressed file
                alt_path = self._get_save_path(slot_id, compressed=True)
                if os.path.exists(alt_path) and alt_path != save_path:
                    os.remove(alt_path)
            
            print(f"[SAVE] Game saved to slot '{slot_id}' (Compressed: {compress})")
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
            path_compressed = self._get_save_path(slot_id, compressed=True)
            path_json = self._get_save_path(slot_id, compressed=False)

            # Determine which file to load
            target_path = None
            is_compressed = False
            
            if os.path.exists(path_compressed) and os.path.exists(path_json):
                # Both exist, check timestamps
                t_comp = os.path.getmtime(path_compressed)
                t_json = os.path.getmtime(path_json)
                if t_comp >= t_json:
                    target_path = path_compressed
                    is_compressed = True
                else:
                    target_path = path_json
                    is_compressed = False
            elif os.path.exists(path_compressed):
                target_path = path_compressed
                is_compressed = True
            elif os.path.exists(path_json):
                target_path = path_json
                is_compressed = False
            else:
                print(f"[ERROR] Save file '{slot_id}' not found")
                return None
            
            if is_compressed:
                with gzip.open(target_path, 'rt', encoding='utf-8') as f:
                    save_data = json.load(f)
            else:
                with open(target_path, 'r', encoding='utf-8') as f:
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
            slot_id = None
            data = None

            try:
                if filename.endswith('.json'):
                    slot_id = filename[:-5]
                    with open(os.path.join(self.save_directory, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                elif filename.endswith('.dat'):
                    slot_id = filename[:-4]
                    with gzip.open(os.path.join(self.save_directory, filename), 'rt', encoding='utf-8') as f:
                        data = json.load(f)

                if data:
                    saves.append({
                        "slot_id": slot_id,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "scene": data.get("scene", "Unknown"),
                        "summary": data.get("summary", "No summary"),
                        "datetime": data.get("datetime", "Unknown"),
                        "compressed": filename.endswith('.dat')
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
            path_compressed = self._get_save_path(slot_id, compressed=True)
            path_json = self._get_save_path(slot_id, compressed=False)

            deleted = False
            if os.path.exists(path_compressed):
                os.remove(path_compressed)
                deleted = True
            
            if os.path.exists(path_json):
                os.remove(path_json)
                deleted = True

            if deleted:
                print(f"[DELETE] Save '{slot_id}' deleted")
                return True
            else:
                print(f"[ERROR] Save file '{slot_id}' not found")
                return False
            
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
