import json
import os
import sys
import random
from typing import Optional

from engine.branch_controller import BranchController

class SceneManager:
    def __init__(self, time_system, board, skill_system, player_state, flashback_manager, clue_system=None):
    def __init__(self, time_system, board, skill_system, player_state, flashback_manager, 
                 npc_system=None, attention_system=None, inventory_system=None):
        self.scenes = {}
        self.current_scene_data = None
        self.current_scene_id = None
        self.time_system = time_system
        self.board = board
        self.skill_system = skill_system
        self.player_state = player_state
        self.flashback_manager = flashback_manager
        self.clue_system = clue_system
        
        # New Systems for Branch Controller
        self.npc_system = npc_system
        self.attention_system = attention_system
        self.inventory_system = inventory_system
        
        self.branch_controller = BranchController()

    def load_scenes_from_directory(self, directory: str, root_scenes: Optional[str] = None):
        # Fallback to finding existing scenes.json in root if directory doesn't look populated
        if not root_scenes:
            root_scenes = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scenes.json")
        
        # Try loading directory first
        if os.path.exists(directory) and os.listdir(directory):
            for filename in os.listdir(directory):
                if filename.endswith(".json"):
                    full_path = os.path.join(directory, filename)
                    self.load_scenes_file(full_path)
            
        # Also load root scenes if needed (or if directory empty)
        if os.path.exists(root_scenes):
             self.load_scenes_file(root_scenes)

    def load_scenes_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle list or single object
                if isinstance(data, list):
                    for scene in data:
                        self.scenes[scene['id']] = scene
                elif isinstance(data, dict):
                    self.scenes[data['id']] = data
        except Exception as e:
            print(f"Error loading scenes from {filename}: {e}")

    def load_scene(self, scene_id):
        scene = self.scenes.get(scene_id)
        if not scene:
            return None

        # Check Conditions
        if not self._check_conditions(scene):
            # If not accessible, return None (Game loop handles "Blocked")
            # For now, simplistic approach
            return None

        self.current_scene_id = scene_id
        self.current_scene_data = scene
        
        # Flashback Handling (Phase 6)
        if scene.get("type") == "flashback":
             pov_data = scene.get("pov_data", {})
             self.flashback_manager.enter_flashback(pov_data)
        elif self.flashback_manager.in_flashback:
             # If we move to a non-flashback scene, exit flashback
             self.flashback_manager.exit_flashback()
        
        # Trigger Memory
        self._check_memory_trigger(scene)
        
        # Apply on-entry effects
        self._apply_on_entry_effects(scene)

        return self.current_scene_data

    def _apply_on_entry_effects(self, scene):
        effects = scene.get("effects")
        if effects:
            # We need a way to communicate these back to Game? 
            # Or just modify player_state directly (which we have a ref to)
            for key, value in effects.items():
                if key == "sanity":
                    self.player_state["sanity"] = max(0, min(100, self.player_state["sanity"] + value))
                    print(f"[SANITY ENTRY CHANGE] {value}")
                elif key == "reality":
                    self.player_state["reality"] = max(0, min(100, self.player_state["reality"] + value))
                    print(f"[REALITY ENTRY CHANGE] {value}")

    def _get_game_state(self):
        """Construct game state dictionary for BranchController."""
        return {
            "board": self.board,
            "skill_system": self.skill_system,
            "player_state": self.player_state,
            "time_system": self.time_system,
            "npc_system": self.npc_system,
            "attention_system": self.attention_system,
            "inventory_system": self.inventory_system,
            "current_location": self.player_state.get("current_location"),
            "location_states": self.player_state.get("location_states", {}),
            "player_flags": self.player_state.get("event_flags", set()),
        }

    def _check_conditions(self, scene) -> bool:
        conditions = scene.get("conditions", {})
        if not conditions:
            return True
            
            # Access datetime object
            current_h = self.time_system.current_time.hour 
            
            if start_h <= end_h:
                if not (start_h <= current_h < end_h):
                    return False
            else: # Overnight e.g. 22:00 to 06:00
                if not (current_h >= start_h or current_h < end_h):
                    return False

        # Weather Check
        if "weather" in conditions:
            allowed = conditions["weather"]
            if self.time_system.weather not in allowed:
                return False

        # Theory Check (Board)
        if "requires_theory" in conditions:
            reqs = conditions["requires_theory"]
            for tid in reqs:
                theory = self.board.get_theory(tid)
                if not theory or theory.status != "active":
                    return False

        # Clue Interpretation Check
        if "clue_interpretation" in conditions:
            # Format: {"clue_id": "foo", "lens": "believer"}
            req = conditions["clue_interpretation"]
            clue_id = req.get("clue_id")
            required_lens = req.get("lens")

            if self.clue_system and clue_id:
                state = self.clue_system.get_acquired_clue(clue_id)
                if not state:
                    return False
                if required_lens and state.current_lens != required_lens:
                    return False

        return True
        game_state = self._get_game_state()
        return self.branch_controller.evaluate_condition(conditions, game_state)

    def _check_memory_trigger(self, scene):
        trigger = scene.get("memory_trigger")
        if not trigger:
            return

        skill_name = trigger.get("skill")
        dc = trigger.get("dc", 10)
        text = trigger.get("text")
        
        # Simple check: Roll every time for now
        print(f"\n[?] Checking memory trigger ({skill_name})...")
        result = self.skill_system.roll_check(skill_name, dc)
        if result["success"]:
            print(f"[MEMORY UNLOCKED] {text}\n")
        
    def get_available_scenes(self):
        if not self.current_scene_data:
            return []
            
        connected_ids = self.current_scene_data.get("connected_scenes", [])
        available = []
        
        game_state = self._get_game_state()
        
        for sid in connected_ids:
            scene = self.scenes.get(sid)
            if not scene: continue
            
            # Use BranchController for check
            conditions = scene.get("conditions", {})
            is_accessible = self.branch_controller.evaluate_condition(conditions, game_state)
            
            available.append({
                "id": sid,
                "name": scene.get("name", "Unknown"),
                "accessible": is_accessible
            })
        return available

    def apply_ambient_effects(self, minutes: int):
        if not self.current_scene_data:
            return

        ambient = self.current_scene_data.get("ambient_effects", {})
        
        # Sanity Drain
        san_drain = ambient.get("sanity_drain_per_min", 0)
        if san_drain > 0:
            total = san_drain * minutes
            self.player_state["sanity"] = max(0, self.player_state["sanity"] - total)
            print(f"[Ambient] The atmosphere weighs on you. Sanity -{total:.1f}")

        # Reality Drain
        real_drain = ambient.get("reality_drain_per_min", 0)
        if real_drain > 0:
            total = real_drain * minutes
            self.player_state["reality"] = max(0, self.player_state["reality"] - total)
            print(f"[Ambient] The world feels thin here. Reality -{total:.1f}")

        # Paranoia
        mult = ambient.get("paranoia_multiplier", 1.0)
        if mult > 1.0 and random.random() < 0.1 * mult:
             print("[Paranoia] Shadows stretch longer than they should.")

    def update_board_effects(self):
        """
        Updates skill modifiers based on active theories in the board.
        """
        if not self.board or not self.skill_system:
            return

        modifiers = self.board.get_all_modifiers()

        # Clear old board modifiers first?
        # Ideally, we should track which modifiers come from board to avoid wiping others.
        # But for now, we'll assume we overwrite/set them by key "Board Theory".

        # Reset board-related modifiers on all skills
        for skill in self.skill_system.skills.values():
            skill.set_modifier("Board Theory", 0)

        # Apply new
        for skill_name, mod_value in modifiers.items():
            skill = self.skill_system.get_skill(skill_name)
            if skill:
                skill.set_modifier("Board Theory", mod_value)
                print(f"[Board Effect] {skill_name} modifier: {mod_value}")
