import json
import os
from typing import Dict, Any, Optional

class SceneManager:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.current_scene: Optional[Dict[str, Any]] = None
        self.scenes_cache: Dict[str, Dict[str, Any]] = {}

    def load_scene(self, scene_id: str) -> Dict[str, Any]:
        """Loads a scene definition from JSON."""
        if scene_id in self.scenes_cache:
            self.current_scene = self.scenes_cache[scene_id]
            return self.current_scene

        # Construct path (assuming flat structure for now)
        file_path = os.path.join(self.data_path, "scenes", f"{scene_id}.json")
        
        # Fallback or error handling
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Scene file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.scenes_cache[scene_id] = data
        self.current_scene = data
        return data

    def get_description(self) -> str:
        if not self.current_scene:
            return "Void."
        return self.current_scene.get("description", "No description available.")

    def get_exits(self) -> Dict[str, str]:
        if not self.current_scene:
            return {}
        return self.current_scene.get("exits", {})

    def get_interactable(self, key: str) -> Optional[str]:
        if not self.current_scene:
            return None
        interactables = self.current_scene.get("interactables", {})
        return interactables.get(key)
