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

    def get_description(self, character: Any = None) -> str:
        if not self.current_scene:
            return "Void."
        
        text_data = self.current_scene.get("text")
        
        # Backward compatibility for simple string
        if isinstance(text_data, str):
            return text_data
            
        if isinstance(text_data, dict):
            base = text_data.get("base", "")
            if not character:
                return base
                
            # Apply Lens
            lens_text = self._apply_lens(text_data.get("lens", {}), character)
            
            # Apply Inserts (Basic check support)
            # This requires evaluating conditions, which we'll simplify for now
            inserts_text = ""
            if "inserts" in text_data:
                for insert in text_data["inserts"]:
                    # check conditions here if possible, for now just skip or simplified
                    pass
                    
            # Combine
            # Logic: If lens text exists, does it replace or append? 
            # Design doc says "filters reality", implying replacement or heavy overlay.
            # But usually it's Base + Lens additions.
            # However, vertical_slice examples show distinct paragraphs.
            # Let's return Base + "\n\n" + Lens
            
            full_text = base
            if lens_text:
                full_text += f"\n\n{lens_text}"
                
            return full_text
            
        return "No description available."

    def _apply_lens(self, lenses: Dict[str, str], character: Any) -> str:
        """
        Maps character attributes to narrative lenses.
        """
        if not lenses:
            return ""

        # Default mapping based on Writer's Guide
        # Note: Accessing attributes from SkillSystem keys (REASON, INTUITION, PRESENCE)
        # Character object might be a dict or object depending on context, assuming object with .attributes
        scores = {}
        if hasattr(character, "attributes"):
            # If it's the SkillSystem or similar object with attributes dict of objects
            # We need the values
            for key, attr_obj in character.attributes.items():
                if hasattr(attr_obj, "value"):
                     scores[key] = attr_obj.value
                else:
                     scores[key] = attr_obj # specific int value
        else:
             # Fallback if character is just a dict (player_state backup?)
             scores = character.get("attributes", {})

        if not scores:
            return ""
        
        # Determine dominant attribute
        dominant = max(scores, key=scores.get)
        
        selected_lens = None
        if dominant == "REASON": # Was RATIONALITY
            selected_lens = "skeptic"
        elif dominant == "INTUITION": # Was SENSITIVITY
            selected_lens = "believer"
        elif dominant == "PRESENCE": 
            selected_lens = "haunted"
        else:
            # Fieldcraft or Constitution -> Skeptic default
            selected_lens = "skeptic"
            
        return lenses.get(selected_lens, "")
            
        return lenses.get(selected_lens, "")

    def get_exits(self) -> Dict[str, str]:
        if not self.current_scene:
            return {}
            
        # Priority 1: Explicit exits
        if "exits" in self.current_scene:
            return self.current_scene["exits"]
            
        # Priority 2: Infer from choices
        choices = self.current_scene.get("choices", [])
        inferred_exits = {}
        for idx, choice in enumerate(choices):
            # Map "1", "2" to next_scene
            inferred_exits[str(idx + 1)] = choice.get("next_scene", "")
            
            # Also try to map first word of label if valid direction?
            # Creating a simple map for "go 1", "go 2"
            
        return inferred_exits

    def get_choices(self):
        """Return the raw choices list."""
        return self.current_scene.get("choices", [])

    def get_interactable(self, key: str) -> Optional[str]:
        if not self.current_scene:
            return None
        interactables = self.current_scene.get("interactables", {})
        # Check objects dict as well (new schema)
        objects = self.current_scene.get("objects", {})
        
        if key in interactables:
            return interactables[key]
            
        if key in objects:
            obj = objects[key]
            if isinstance(obj, dict):
                return obj.get("description", "")
            return str(obj)
            
        return None
