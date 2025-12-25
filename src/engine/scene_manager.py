import json
import os
import sys
import random
from typing import Optional, Dict, Any

class SceneManager:
    def __init__(self, time_system, board, skill_system, player_state, flashback_manager):
        self.scenes = {}
        self.current_scene_data = None
        self.current_scene_id = None
        self.time_system = time_system
        self.board = board
        self.skill_system = skill_system
        self.player_state = player_state
        self.flashback_manager = flashback_manager

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

        # Check Access Conditions (Conditions + Exit Conditions of previous scene potentially?)
        # NOTE: Game.py should probably call check_exit_conditions before allowing navigation away.
        # But here we assume if we are loading it, we are trying to enter.

        if not self._check_conditions(scene):
            # If not accessible, return None (Game loop handles "Blocked")
            return None

        self.current_scene_id = scene_id
        
        # Normalize Scene Data: Merge dynamic_inserts into text.inserts
        self.current_scene_data = self._normalize_scene_data(scene)

        # Flashback Handling
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

    def _normalize_scene_data(self, scene_data: dict) -> dict:
        """
        Pre-process scene data to merge modular dynamic_inserts into the format
        TextComposer expects.
        """
        # Copy to avoid mutating original
        scene = scene_data.copy()

        # Handle dynamic_inserts
        if "dynamic_inserts" in scene:
            text_data = scene.get("text", {})
            # Ensure text_data is a dict
            if isinstance(text_data, str):
                text_data = {"base": text_data}

            existing_inserts = text_data.get("inserts", [])
            new_inserts = []

            for d_insert in scene["dynamic_inserts"]:
                trigger = d_insert.get("trigger")
                parsed_condition = self._parse_trigger_string(trigger)

                new_inserts.append({
                    "id": d_insert.get("id", f"dyn_{random.randint(1000,9999)}"),
                    "text": d_insert.get("text", ""),
                    "insert_at": d_insert.get("insert_at", "AFTER_BASE"),
                    "condition": parsed_condition
                })

            text_data["inserts"] = existing_inserts + new_inserts
            scene["text"] = text_data

        return scene

    def _parse_trigger_string(self, trigger: Any) -> Dict:
        """
        Convert a trigger string (e.g. "Skill > 5") or object into TextComposer condition dict.
        """
        if isinstance(trigger, dict):
            return trigger

        if not isinstance(trigger, str):
            return {}

        # Simple parser for "Attribute Operator Value" or function-like calls
        trigger = trigger.strip()

        # Case 1: has_item('item_name')
        if trigger.startswith("has_item("):
            item_name = trigger[9:-1].strip("'\"")
            return {"equipment": item_name} # TextComposer uses 'equipment' key

        # Case 2: Skill > Value
        if ">" in trigger:
            parts = trigger.split(">")
            if len(parts) == 2:
                skill = parts[0].strip()
                try:
                    val = int(parts[1].strip())
                    return {"skill_gte": {skill: val}} # Assuming > is >= or close enough
                except ValueError:
                    pass

        # TODO: Add more parsers as needed
        return {}

    def _apply_on_entry_effects(self, scene):
        # 1. Standard Effects
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

        # 2. Event Flags
        event_flags = scene.get("event_flags", [])
        for flag in event_flags:
            self.player_state["event_flags"].add(flag)

    def check_parser_triggers(self, verb: str, target: str) -> Optional[dict]:
        """
        Check if the player's input triggers a special event in the current scene.
        """
        if not self.current_scene_data:
            return None

        triggers = self.current_scene_data.get("parser_triggers", [])
        if not triggers:
            return None

        full_command = f"{verb} {target}".strip().lower()

        for trigger in triggers:
            # Check command match
            t_cmd = trigger.get("command", "").lower()
            if full_command == t_cmd or (verb.lower() == t_cmd and not target):
                # Check required flags
                req_flags = trigger.get("required_flags", [])
                if req_flags:
                    player_flags = self.player_state.get("event_flags", set())
                    if not all(f in player_flags for f in req_flags):
                        continue

                # Trigger matches!
                return trigger

        return None

    def check_exit_conditions(self, target_scene_id: str) -> Optional[str]:
        """
        Check if leaving the scene is blocked.
        Returns None if allowed, or a message string if blocked.
        """
        if not self.current_scene_data:
            return None

        exits = self.current_scene_data.get("exit_conditions", [])
        for condition in exits:
            # Check if this condition applies to the target (or all if target is "*")
            t_target = condition.get("target", "*")
            if t_target != "*" and t_target != target_scene_id:
                continue

            cond_str = condition.get("condition", "")

            # Parse condition
            blocked = False

            # "requires_flag('flag_name')"
            if cond_str.startswith("requires_flag("):
                flag = cond_str[14:-1].strip("'\"")
                if flag not in self.player_state.get("event_flags", set()):
                    blocked = True

            # "theory_active('theory_id')"
            elif cond_str.startswith("theory_active("):
                tid = cond_str[14:-1].strip("'\"")
                theory = self.board.get_theory(tid)
                if not theory or theory.status != "active":
                    blocked = True

            # "sanity_lt(20)"
            elif cond_str.startswith("sanity_lt("):
                try:
                    val = int(cond_str[10:-1])
                    if self.player_state["sanity"] >= val:
                        blocked = True # Blocked if sanity is NOT low enough? Or implies "Locked if sanity < 20"?
                        # Usually "condition" implies "requirement to PASS".
                        # But exit_conditions usually define BLOCKS.
                        # Let's assume "condition" is the BLOCK condition.
                        pass
                except ValueError:
                    pass

            if blocked:
                return condition.get("locked_message", "The way is blocked.")

        return None

    def _check_conditions(self, scene) -> bool:
        conditions = scene.get("conditions", {})
        
        # Time Check
        if "time" in conditions:
            # Format "HH:MM", currently only checking hours for simplicity
            start_str, end_str = conditions["time"]
            start_h = int(start_str.split(":")[0])
            end_h = int(end_str.split(":")[0])
            
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

        return True

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
        
        for sid in connected_ids:
            scene = self.scenes.get(sid)
            if not scene: continue
            
            is_accessible = self._check_conditions(scene)
            
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
