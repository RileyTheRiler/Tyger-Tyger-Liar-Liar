
import sys
import os
import time
import random

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mechanics import SkillSystem, CharacterSheetUI
from board import Board
from time_system import TimeSystem
from endgame_manager import EndgameManager
from scene_manager import SceneManager
from input_system import CommandParser, InputMode
from dialogue_manager import DialogueManager
from src.inventory_system import InventoryManager, Item, Evidence
from src.save_system import EventLog, SaveSystem
from interface import print_separator, print_boxed_title, print_numbered_list, format_skill_result

class Game:
    def __init__(self):
        # Initialize Systems
        self.time_system = TimeSystem()
        self.board = Board()
        self.skill_system = SkillSystem()
        self.char_ui = CharacterSheetUI(self.skill_system)
        self.inventory_system = InventoryManager()
        self.event_log = EventLog()
        self.save_system = SaveSystem()
        self.parser = CommandParser()
        self.input_mode = InputMode.INVESTIGATION 
        self.debug_mode = False
        self.last_autosave_time = 0
        
        # Link Time System to Board
        self.time_system.add_listener(self.on_time_passed)
        
        # Player State
        self.player_state = {
            "sanity": 100.0,
            "reality": 100.0,
            "inventory": [],
            "thoughts": [],
            "injuries": []
        }

        # Initialize Scene Manager
        self.scene_manager = SceneManager(
            self.time_system, 
            self.board, 
            self.skill_system, 
            self.player_state
        )
        
        # Initialize Dialogue Manager
        self.dialogue_manager = DialogueManager(
            self.skill_system,
            self.board,
            self.player_state
        )
        self.in_dialogue = False
        
        # Load Scenes
        scenes_dir = os.path.join(os.path.dirname(__file__), 'data', 'scenes')
        self.scene_manager.load_scenes_from_directory(scenes_dir)

    def on_time_passed(self, minutes: int):
        msgs = self.board.on_time_passed(minutes)
        if msgs:
            print("\n*** BOARD UPDATE ***")
            for m in msgs:
                print(f" -> {m}")
            print("********************\n")
        
        # Update Modifiers
        self.update_board_effects()
        
        # Apply Scene Ambient Effects
        if self.scene_manager.current_scene_data:
            self.scene_manager.apply_ambient_effects(minutes)
            
        # Recovery / Injury Checks
        self.process_recovery(minutes)

    def process_recovery(self, minutes: int):
        injuries = self.player_state.get("injuries", [])
        healed = []
        for injury in injuries:
            injury["healing_time_remaining"] -= minutes
            if injury["healing_time_remaining"] <= 0:
                healed.append(injury)
        
        for h in healed:
            injuries.remove(h)
            print(f"\n[RECOVERY] Your '{h['name']}' has healed properly.")
            # Restore stats if needed?


    def update_board_effects(self):
        # Clear old Board modifiers (hacky reset for now)
        for skill in self.skill_system.skills.values():
            skill.set_modifier("Board", 0)
            
        current_mods = self.board.get_all_modifiers()
        for skill_name, val in current_mods.items():
            skill = self.skill_system.get_skill(skill_name)
            if skill:
                skill.set_modifier("Board", val)

    def run(self, start_scene_id):
        # Initial Load
        scene = self.scene_manager.load_scene(start_scene_id)
        if not scene:
            print("Failed to load initial scene.")
            return
        
        # Log initial scene entry
        # self.log_event("scene_entry", scene_id=start_scene_id, scene_name=scene.get("name", "Unknown"))

        while True:
            # Check autosave
            # self.check_autosave()
            
            # Check for Breakdowns
            if self.player_state["sanity"] <= 0:
                print("\n>> SANITY CRITICAL: You collapse under the weight of your own mind. <<")
                self.player_state["sanity"] = 10 
                self.log_event("breakdown", breakdown_type="sanity")
                # Ideally move to a dream scene
                continue

            if self.player_state["reality"] <= 0:
                print("\n>> REALITY FRACTURE: The world dissolves. Who are you? <<")
                self.player_state["reality"] = 10
                self.log_event("breakdown", breakdown_type="reality")
                # Ideally move to fracture scene
                continue

            if self.in_dialogue:
                self.run_dialogue_loop()
            else:
                self.display_scene()
                
                choices = self.scene_manager.current_scene_data.get("choices", [])
                
                # Passive Interrupts
                interrupts = self.skill_system.check_passive_interrupts(
                    self.scene_manager.current_scene_data["text"],
                    self.player_state["sanity"]
                )
                if interrupts:
                    print("\n" + "~" * 60)
                    for msg in interrupts:
                        print(f" {msg}")
                    print("~" * 60)

                self.display_status_line()
                
                action = self.get_player_input(choices)
                
                if action == "quit":
                    break
                elif action == "refresh":
                    continue
                elif isinstance(action, dict):
                    # Check for dialogue trigger
                    if "type" in action and action["type"] == "dialogue":
                        dialogue_id = action.get("dialogue_id")
                        if dialogue_id:
                            self.start_dialogue(dialogue_id)
                            continue
                    
                    # Transitions
                    next_id = self.process_choice(action)
                    if next_id:
                         # Load next scene
                         new_scene = self.scene_manager.load_scene(next_id)
                         if not new_scene:
                             print(f"Cannot move to {next_id} (Locked or Missing).")
                         else:
                             # Log scene entry
                             self.log_event("scene_entry", scene_id=next_id, scene_name=new_scene.get("name", "Unknown"))

    def display_status_line(self):
        mode_str = "DIALOGUE" if self.input_mode == InputMode.DIALOGUE else "INVESTIGATION"
        debug_str = " [DEBUG]" if self.debug_mode else ""
        print_separator("-", 64)
        print(f"[{mode_str} MODE{debug_str}] - (b)oard, (c)haracter, (i)nventory, (e)vidence")
        print("                   (w)ait, (s)leep, (h)elp, (q)uit, [switch]")
        print_separator("-", 64)

    def apply_reality_distortion(self, text):
        reality = self.player_state["reality"]
        if reality >= 75:
            return text
            
        # Level 1 Distortion (74-50): Minor sensory additions
        if reality < 75 and reality >= 50:
            if random.random() < 0.3:
                text += " (Did the shadows just move?)"
                
        # Level 2 Distortion (49-25): Word replacements
        if reality < 50:
            replacements = {
                "door": "mouth",
                "window": "eyes",
                "light": "burning gaze",
                "shadow": "living void",
                "tree": "reaching hand",
                "sky": "infinite abyss",
                "wall": "skin",
                "floor": "flesh"
            }
            words = text.split()
            new_words = []
            for word in words:
                lower_word = word.lower().strip('.,!?')
                if lower_word in replacements and random.random() < 0.4:
                    new_words.append(replacements[lower_word].upper())
                else:
                    new_words.append(word)
            text = " ".join(new_words)

        # Level 3 Distortion (<25): Hallucinated sentences
        if reality < 25:
            if random.random() < 0.5:
                text += "\nTHEY ARE WATCHING YOU."
        
        return text

    def display_scene(self):
        scene = self.scene_manager.current_scene_data
        print("\n" + "="*60)
        
        # HUD
        san = self.player_state["sanity"]
        real = self.player_state["reality"]
        san_status = "STABLE" if san >= 75 else "UNSETTLED" if san >= 50 else "HYSTERIA" if san >= 25 else "PSYCHOSIS"
        real_status = "LUCID" if real >= 75 else "DOUBT" if real >= 50 else "DELUSION" if real >= 25 else "BROKEN"

        print_separator("=")
        print(f"TIME: {self.time_system.get_time_string()} | SANITY: {san:.0f}% ({san_status}) | REALITY: {real:.0f}% ({real_status})")
        print_separator("=")
        
        print_boxed_title(scene.get("name", "Unknown Area"))
        
        if scene.get("background_media"):
            media = scene["background_media"]
            print(f"[MEDIA: Loading {media['type']} '{media['src']}']")
        
        display_text = self.apply_reality_distortion(scene["text"])
        print("\n" + display_text + "\n")
        
        # Show specific ambient indicators
        if "ambient_effects" in scene:
            amb = scene["ambient_effects"]
            if amb.get("sanity_drain_per_min", 0) > 0:
                print("* The atmosphere is oppressive. *")

    def get_player_input(self, choices):
        # List Choices (Dialogue Mode or Hybrid)
        if choices:
            print_numbered_list("CHOICES", choices)
        
        # List Connected Scenes (Spatial Movement) - only if Investigation? Or always?
        connected = self.scene_manager.get_available_scenes()
        offset = len(choices)
        if connected and self.input_mode == InputMode.INVESTIGATION:
            paths = []
            for route in connected:
                status = "" if route["accessible"] else "(BLOCKED)"
                paths.append(f"Go to {route['name']} {status}")
            print_numbered_list("PATHS", paths, offset=offset)

        while True:
            raw = input("\n> ").strip()
            if not raw:
                continue
            
            # Handle special commands first
            clean = raw.lower()
            if clean in ['q', 'quit', 'exit']:
                return "quit"
            if clean in ['b', 'board']:
                self.show_board()
                return "refresh"
            if clean in ['c', 'character', 'sheet']:
                self.char_ui.display()
                return "refresh"
            if clean in ['switch', 'swap']:
                self.toggle_mode()
                return "refresh"
            if clean in ['h', 'help', '?']:
                self.handle_parser_command("HELP", None)
                return "refresh"
            
            # Inventory & Evidence Commands
            if clean in ['i', 'inventory', 'inv']:
                self.inventory_system.list_inventory()
                return "refresh"
            if clean in ['e', 'evidence']:
                self.inventory_system.view_board()
                return "refresh"
            
            # Wait Command
            if clean in ['w', 'wait']:
                try:
                     mins = int(input("Wait for how many minutes? > "))
                     if mins > 0:
                         print(f"... Waiting {mins} minutes ...")
                         self.time_system.advance_time(mins)
                         return "refresh"
                except ValueError:
                    print("Invalid number.")
                    continue
            
            # Sleep Command
            if clean in ['s', 'sleep']:
                print("... Sleeping (8 hours) ...")
                # Advance 8 hours
                self.time_system.advance_time(8 * 60)
                # Recover sanity/stats here if needed
                self.player_state['sanity'] = min(self.player_state['sanity'] + 20, 100)
                print("You wake up feeling rested. (+20 Sanity)")
                return "refresh"
            
            # Debug Mode Commands
            if clean == 'debug':
                self.debug_mode = not self.debug_mode
                print(f"[DEBUG MODE: {'ON' if self.debug_mode else 'OFF'}]")
                return "refresh"
            
            if self.debug_mode:
                # Debug: Force Save
                if clean.startswith('forcesave'):
                    parts = clean.split()
                    slot = parts[1] if len(parts) > 1 else "debug_save"
                    self.save_game(slot)
                    return "refresh"
                
                # Debug: Export Save
                if clean.startswith('export'):
                    parts = clean.split()
                    if len(parts) >= 3:
                        slot = parts[1]
                        path = parts[2]
                        self.save_system.export_save(slot, path)
                    else:
                        print("Usage: export <slot_id> <output_path>")
                    return "refresh"
                
                # Debug: Set Sanity/Reality
                if clean.startswith('set'):
                    parts = clean.split()
                    if len(parts) >= 3:
                        stat = parts[1]
                        value = float(parts[2])
                        if stat in self.player_state:
                            self.player_state[stat] = value
                            print(f"[DEBUG] {stat} set to {value}")
                    return "refresh"
                
                # Debug: Add XP
                if clean.startswith('addxp'):
                    parts = clean.split()
                    if len(parts) >= 2:
                        xp = int(parts[1])
                        self.skill_system.add_xp(xp)
                        print(f"[DEBUG] Added {xp} XP")
                    return "refresh"
                
                # Debug: Teleport to scene
                if clean.startswith('goto'):
                    parts = clean.split()
                    if len(parts) >= 2:
                        scene_id = parts[1]
                        new_scene = self.scene_manager.load_scene(scene_id)
                        if new_scene:
                            print(f"[DEBUG] Teleported to {scene_id}")
                            self.log_event("scene_entry", scene_id=scene_id, scene_name=new_scene.get("name", "Unknown"))
                        else:
                            print(f"[DEBUG] Scene '{scene_id}' not found")
                    return "refresh"
                
            # Numeric Choices
            if raw.isdigit():
                idx = int(raw) - 1
                
                # Check scene choices
                if 0 <= idx < len(choices):
                    return choices[idx]
                
                # Check connected paths (only in Investigation mode?)
                if self.input_mode == InputMode.INVESTIGATION:
                    path_idx = idx - len(choices)
                    if 0 <= path_idx < len(connected):
                        route = connected[path_idx]
                        if route["accessible"]:
                            return {"next_scene_id": route["id"]}
                        else:
                            print("That path is blocked.")
                            return "refresh"
                
                print("Invalid choice number.")
                continue

            # Parser Handling
            if self.input_mode == InputMode.INVESTIGATION:
                verb, target = self.parser.normalize(raw)
                if verb:
                    self.handle_parser_command(verb, target)
                    return "refresh" # Stay in same scene
                else:
                    print("I don't understand that command.")
            else:
                print("Use numbered choices in Dialogue Mode (or type 'switch').")

    def toggle_mode(self):
        if self.input_mode == InputMode.DIALOGUE:
            self.input_mode = InputMode.INVESTIGATION
            print("[Switched to INVESTIGATION mode]")
        else:
            self.input_mode = InputMode.DIALOGUE
            print("[Switched to DIALOGUE mode]")

    def handle_parser_command(self, verb, target):
        scene = self.scene_manager.current_scene_data
        objects = scene.get("objects", {})
        
        print(f"\n[ACTION: {verb} {target}]")

        if verb == "EXAMINE":
            if not target:
                print("Examine what?")
                return
            
            # Improved fuzzy match for target in objects
            obj_data = objects.get(target)
            if not obj_data:
                # Try partial match (key contains target)
                for k in objects.keys():
                    if target in k or k in target:
                        obj_data = objects[k]
                        print(f"(Assuming you meant '{k}')")
                        break
            
            if obj_data:
                desc = obj_data.get("description", "You see nothing special.")
                print(f"{desc}")
                
                # Passive Checks
                if "passive_checks" in obj_data:
                    for check in obj_data["passive_checks"]:
                        # Silent check: 2d6 + Skill >= DC
                        skill_name = check["skill"]
                        dc = check["difficulty"]
                        
                        # We use 'roll_check' but treat it silently unless success
                        result = self.skill_system.roll_check(skill_name, dc, manual_roll=None)
                        if result["success"]:
                            print(f"\n[{skill_name.upper()} SUCCESS] {check['success_text']}")

                # Interactions
                if "interactions" in obj_data:
                    print(f"You could also: {', '.join(obj_data['interactions'].keys()).upper()}")
            else:
                print(f"You don't see '{target}' here.")

        elif verb == "USE":
             # Need specific interaction logic
             found = False
             for obj_name, obj_data in objects.items():
                 if obj_name == target or target in obj_name:
                     inters = obj_data.get("interactions", {})
                     
                     if "use" in inters:
                         print(inters["use"])
                         found = True
                     break
             if not found:
                 print(f"You can't use the {target} like that.")

        elif verb == "HELP":
            print("\n-=- AVAILABLE COMMANDS -=-")
            print(" INVESTIGATION: EXAMINE [target], USE [target], GO [target], TAKE [target]")
            print(" SYSTEM: (b)oard, (c)haracter, (i)nventory, (e)vidence, (w)ait, (s)leep, (q)uit")
            print(" NAVIGATION: Type the number of a choice or path.")
            print("--------------------------")

        elif verb == "INVENTORY":
            self.inventory_system.list_inventory()

        else:
            print(f"You try to {verb} the {target or 'air'}, but nothing happens yet.")

    def apply_effects(self, effects):
        if not effects: return
        
        for key, value in effects.items():
            if key == "sanity":
                self.player_state["sanity"] = max(0, min(100, self.player_state["sanity"] + value))
                print(f"[SANITY {'+' if value > 0 else ''}{value}]")
            elif key == "reality":
                self.player_state["reality"] = max(0, min(100, self.player_state["reality"] + value))
                print(f"[REALITY {'+' if value > 0 else ''}{value}]")
            elif key == "xp":
                print(f"[XP +{value}]")
            elif key == "unlock_thought":
                if value not in self.player_state["thoughts"]:
                    self.player_state["thoughts"].append(value)
                    print(f"[THOUGHT UNLOCKED: {value}]")
    
    def save_game(self, slot_id: str, auto=False):
        """Save the current game state."""
        try:
            # Gather all state data
            state_data = {
                "scene": self.scene_manager.current_scene_id if self.scene_manager.current_scene_id else "bedroom",
                "datetime": self.time_system.current_time.strftime("%Y-%m-%d %H:%M"),
                "summary": self._generate_save_summary(),
                "character_state": {
                    "skill_system": self.skill_system.to_dict(),
                    "player_state": self.player_state.copy(),
                },
                "board_state": self.board.to_dict(),
                "inventory": self.inventory_system.to_dict(),
                "time_system": self.time_system.to_dict(),
                "event_log": self.event_log.to_dict(),
                "scene_state": {
                    "current_scene_id": self.scene_manager.current_scene_id,
                    "visited_scenes": list(self.scene_manager.visited_scenes) if hasattr(self.scene_manager, 'visited_scenes') else []
                }
            }
            
            success = self.save_system.save_game(slot_id, state_data)
            
            if success and not auto:
                print(f"\n✓ Game saved successfully to '{slot_id}'")
            elif success and auto:
                print(f"[AUTOSAVE] Game saved to '{slot_id}'")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Failed to save game: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
    
    def load_game(self, slot_id: str):
        """Load a saved game state."""
        try:
            save_data = self.save_system.load_game(slot_id)
            
            if not save_data:
                return False
            
            # Restore skill system
            if "character_state" in save_data and "skill_system" in save_data["character_state"]:
                self.skill_system = SkillSystem.from_dict(save_data["character_state"]["skill_system"])
                self.char_ui = CharacterSheetUI(self.skill_system)
            
            # Restore player state
            if "character_state" in save_data and "player_state" in save_data["character_state"]:
                self.player_state = save_data["character_state"]["player_state"]
            
            # Restore board
            if "board_state" in save_data:
                self.board = Board.from_dict(save_data["board_state"])
            
            # Restore time system
            if "time_system" in save_data:
                self.time_system = TimeSystem.from_dict(save_data["time_system"])
                # Re-register listener
                self.time_system.add_listener(self.on_time_passed)
            
            # Restore inventory
            if "inventory" in save_data:
                self.inventory_system = InventoryManager.from_dict(save_data["inventory"])
            
            # Restore event log
            if "event_log" in save_data:
                self.event_log = EventLog.from_dict(save_data["event_log"])
            
            # Restore scene
            if "scene" in save_data:
                self.scene_manager.load_scene(save_data["scene"])
            
            print(f"\n✓ Game loaded successfully from '{slot_id}'")
            print(f"   Location: {save_data.get('scene', 'Unknown')}")
            print(f"   Time: {save_data.get('datetime', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load game: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
    
    def show_saves(self):
        """Display all available save files."""
        saves = self.save_system.list_saves()
        
        if not saves:
            print("\n[No save files found]")
            return
        
        print("\n" + "="*60)
        print("AVAILABLE SAVES")
        print("="*60)
        
        for save in saves:
            print(f"\nSlot: {save['slot_id']}")
            print(f"  Saved: {save['timestamp']}")
            print(f"  Location: {save['scene']}")
            print(f"  Time: {save['datetime']}")
            print(f"  Summary: {save['summary']}")
        
        print("="*60 + "\n")
    
    def show_event_log(self, limit=20):
        """Display recent events from the event log."""
        events = self.event_log.get_logs(limit=limit)
        
        if not events:
            print("\n[Event log is empty]")
            return
        
        print("\n" + "="*60)
        print("EVENT LOG (Most Recent)")
        print("="*60)
        
        for event in events:
            timestamp = event.get("timestamp", "Unknown")
            event_type = event.get("type", "unknown")
            
            print(f"\n[{timestamp}] {event_type.upper()}")
            
            # Display event-specific details
            if event_type == "scene_entry":
                print(f"  → Entered: {event.get('scene_id', 'Unknown')}")
            elif event_type == "skill_check":
                skill = event.get("skill", "Unknown")
                result = "SUCCESS" if event.get("success") else "FAILURE"
                dc = event.get("difficulty", "?")
                print(f"  → {skill} check (DC {dc}): {result}")
            elif event_type == "theory":
                action = event.get("action", "unknown")
                theory = event.get("theory_name", "Unknown")
                print(f"  → Theory {action}: {theory}")
            elif event_type == "combat":
                print(f"  → {event.get('description', 'Combat event')}")
            else:
                # Generic display
                for key, value in event.items():
                    if key not in ["timestamp", "type"]:
                        print(f"  → {key}: {value}")
        
        print("="*60 + "\n")
    
    def _generate_save_summary(self):
        """Generate a brief summary of current game state for save metadata."""
        scene_name = "Unknown location"
        if self.scene_manager.current_scene_data:
            scene_name = self.scene_manager.current_scene_data.get("name", "Unknown")
        
        active_theories = self.board.get_active_or_internalizing_count()
        
        return f"{scene_name} | {active_theories} active theories"
    
    def check_autosave(self):
        """Check if autosave should trigger (every 15 minutes of game time)."""
        # Stub: save_system removed
        pass
    
    def log_event(self, event_type: str, **details):
        """Log a significant game event."""
        self.event_log.add_event(event_type, details)

    def process_choice(self, choice):
        # Handle Skill Checks
        # Mapped to 'skill_check' per scenes.json
        if "skill_check" in choice:
            check_data = choice["skill_check"]
            success, result_data = self.process_skill_check_result(check_data)
            
            # Helper to extract next scene from result dict
            def get_next_id(data):
                if not data: return None
                return data.get("next_scene")

            if success:
                tgt_data = check_data.get("on_success")
                if tgt_data and "effects" in tgt_data:
                    self.apply_effects(tgt_data["effects"])
                return get_next_id(tgt_data)
            else:
                tgt_data = check_data.get("on_fail")
                if tgt_data and "effects" in tgt_data:
                    self.apply_effects(tgt_data["effects"])
                return get_next_id(tgt_data)

        # Standard transition
        if "effects" in choice:
            self.apply_effects(choice["effects"])
            
        if "next_scene" in choice:
             return choice["next_scene"]
            
        return None

    def process_skill_check_result(self, check_data):
        skill_name = check_data.get("skill")
        difficulty = check_data.get("difficulty", 10)
        
        print(f"\n[Skill Check: {skill_name} (DC {difficulty})]")
        
        # Check Inventory Modifiers
        inv_mod = self.inventory_system.get_modifiers_for_skill(skill_name)
        if inv_mod != 0:
            print(f"[Inventory Modifier: {'+' if inv_mod > 0 else ''}{inv_mod}]")
        
        result = self.skill_system.roll_check(skill_name, difficulty)
        
        # Apply inventory bonus
        result['inventory_mod'] = inv_mod
        result['total'] += inv_mod
        result['success'] = result['total'] >= difficulty
        
        format_skill_result(result)

        if result['success']:
            self.log_event("skill_check", skill=skill_name, difficulty=difficulty, success=True, total=result['total'])
            return True, result
        else:
            self.log_event("skill_check", skill=skill_name, difficulty=difficulty, success=False, total=result['total'])
            return False, result

    def start_dialogue(self, dialogue_id):
        print(f"\n... Entering Dialogue: {dialogue_id} ...")
        dialogues_dir = os.path.join(os.path.dirname(__file__), 'data', 'dialogues')
        if self.dialogue_manager.load_dialogue(dialogue_id, dialogues_dir):
            self.in_dialogue = True
        else:
            print("Failed to start dialogue.")

    def run_dialogue_loop(self):
        data = self.dialogue_manager.get_render_data()
        if not data:
            self.in_dialogue = False
            return

        print("\n" + "-"*40)
        print(f"[{data['speaker']}]: \"{data['text']}\"")
        
        for interjection in data['interjections']:
            print(f" > {interjection}")
            
        print("-" * 40)
        
        choices = data['choices']
        for idx, c in enumerate(choices):
            status = "" if c['enabled'] else f"(BLOCKED {c['reason']})"
            print(f"{idx+1}. {c['text']} {status}")
            
        print("\n(Enter Number, or /debug to toggle hidden)")
        
        raw = input("D> ").strip()
        if raw == "/debug":
            self.dialogue_manager.toggle_debug()
            return

        if not raw.isdigit():
            return
            
        idx = int(raw) - 1
        success, msg = self.dialogue_manager.select_choice(idx)
        
        if success:
            if msg == "EXIT":
                self.in_dialogue = False
                print("... Dialogue Ended ...")
            elif msg.startswith("SCENE:"):
                # If scene request
                scene_id = msg.split(":")[1]
                self.in_dialogue = False
                self.scene_manager.load_scene(scene_id)
        else:
            print(f"Cannot do that: {msg}")

    def show_board(self):
        print("\n=== THE BOARD ===")
        print(f"Slots: {self.board.get_active_or_internalizing_count()}/{self.board.max_slots}")
        for t in self.board.theories.values():
            if t.status in ["active", "internalizing"]:
                 print(f" * {t.name} [{t.status.upper()}]")
        print("=================\n")

    def apply_effects(self, effects):
        for key, value in effects.items():
            if key == "sanity":
                self.player_state["sanity"] += value
                print(f"[Sanity {'+' if value > 0 else ''}{value}]")
            elif key == "reality":
                self.player_state["reality"] += value
                print(f"[Reality {'+' if value > 0 else ''}{value}]")
            elif key == "add_item":
                item = Item.from_dict(value)
                self.inventory_system.add_item(item)
            elif key == "add_evidence":
                ev = Evidence.from_dict(value)
                self.inventory_system.add_evidence(ev)
            elif key == "unlock_thought":
                if value not in self.player_state["thoughts"]:
                    self.player_state["thoughts"].append(value)
                    print(f"[THOUGHT UNLOCKED: {value}]")

if __name__ == "__main__":
    game = Game()
    start_id = sys.argv[1] if len(sys.argv) > 1 else "bedroom"
    game.run(start_id)
