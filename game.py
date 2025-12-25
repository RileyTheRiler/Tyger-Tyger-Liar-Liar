
import sys
import os
import time
import random

# Ensure src is in path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    return path

sys.path.append(resource_path('src'))

from mechanics import SkillSystem, CharacterSheetUI
from board import Board
from board_ui import BoardUI
from lens_system import LensSystem
from attention_system import AttentionSystem
from integration_system import IntegrationSystem
from time_system import TimeSystem
from endgame_manager import EndgameManager
from memory_system import MemorySystem
from scene_manager import SceneManager
from input_system import CommandParser, InputMode
from dialogue_manager import DialogueManager
from combat import CombatManager
from corkboard_minigame import CorkboardMinigame
from src.inventory_system import InventoryManager, Item, Evidence
from src.save_system import EventLog, SaveSystem
from src.journal_system import JournalManager
from interface import print_separator, print_boxed_title, print_numbered_list, format_skill_result

# New GDD-aligned systems
from src.npc_system import NPCSystem
from src.condition_system import ConditionSystem
from src.population_system import PopulationSystem
from src.clue_system import ClueSystem
from src.text_composer import TextComposer, Archetype
from src.fracture_system import FractureSystem, UnsafeMenu
from src.dice import DiceSystem

class Game:
    def __init__(self):
        # Initialize Systems
        self.time_system = TimeSystem()
        self.board = Board()
        self.board_ui = BoardUI(self.board)
        self.skill_system = SkillSystem(resource_path(os.path.join('data', 'skills.json')))
        self.attention_system = AttentionSystem()
        # LensSystem initialized after player_state (see below)
        self.integration_system = IntegrationSystem()
        self.char_ui = CharacterSheetUI(self.skill_system)
        self.inventory_system = InventoryManager()
        self.corkboard = CorkboardMinigame(self.board, self.inventory_system)
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
            "injuries": [],
            "moral_corruption_score": 0,
            "critical_choices": [],
            "suppressed_memories_unlocked": [],
            "event_flags": set(),
            "playtime_minutes": 0,
            "failed_reds": [],
            "checked_whites": []
        }

        # Initialize LensSystem with player_state and attention_system for Haunted lens
        self.lens_system = LensSystem(
            self.skill_system,
            self.board,
            self.player_state,
            self.attention_system
        )

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
        
        # Initialize Endgame and Memory Systems
        self.endgame_manager = EndgameManager(self.board, self.player_state, self.skill_system)
        self.memory_system = MemorySystem(resource_path(os.path.join('data', 'memories', 'memories.json')))
        
        # Initialize Combat Manager
        self.combat_manager = CombatManager(self.skill_system, self.player_state)
        
        # Initialize Journal Manager (Week 6)
        self.journal = JournalManager()

        # === NEW GDD-ALIGNED SYSTEMS ===

        # NPC System - Trust/Fear tracking
        npcs_dir = resource_path(os.path.join('data', 'npcs'))
        self.npc_system = NPCSystem(npcs_dir)

        # Condition System - Injuries and treatments
        conditions_dir = resource_path(os.path.join('data', 'conditions'))
        self.condition_system = ConditionSystem(conditions_dir)

        # Population System - 347 tracking
        self.population_system = PopulationSystem()

        # Clue System - Passive perception and Board integration
        clues_dir = resource_path(os.path.join('data', 'clues'))
        self.clue_system = ClueSystem(clues_dir, self.board)

        # Text Composer - Bad Blood narrative engine
        self.text_composer = TextComposer(self.skill_system, self.board)

        # Fracture System - Reality glitches and unsafe menu
        self.fracture_system = FractureSystem()
        self.unsafe_menu = UnsafeMenu(self.fracture_system)

        # Enhanced Dice System - Manual roll and partial success
        self.dice_system = DiceSystem()

        # Current player archetype (for text composition)
        self.player_archetype = Archetype.NEUTRAL

        # Load Scenes
        scenes_dir = resource_path(os.path.join('data', 'scenes'))
        root_scenes = resource_path('scenes.json')
        self.scene_manager.load_scenes_from_directory(scenes_dir, root_scenes)

    def on_time_passed(self, minutes: int):
        msgs = self.board.on_time_passed(minutes)
        if msgs:
            print("\n*** BOARD UPDATE ***")
            for m in msgs:
                print(f" -> {m}")
            print("********************\n")
        
        # Attention decay
        hours = minutes / 60.0
        self.attention_system.decay_attention(hours)
        
        # Integration progression
        self.integration_system.update_from_attention(self.attention_system.attention_level)
        stage_info = self.integration_system.get_stage_info()
        
        # Apply integration sanity/reality drain
        if stage_info['sanity_drain'] > 0:
            drain = stage_info['sanity_drain'] * hours
            self.player_state['sanity'] -= drain
        if stage_info.get('reality_drain', 0) > 0:
            drain = stage_info['reality_drain'] * hours
            self.player_state['reality'] -= drain
        
        # Check for stage advancement
        if self.integration_system.integration_progress >= 100:
            result = self.integration_system.advance_stage()
            if result:
                print(f"\n*** INTEGRATION STAGE {result['stage']}: {result['name']} ***")
                print(f"{result['description']}")
                if result.get('game_over'):
                    print("\n=== GAME OVER: INTEGRATED ===\n")
                    return  # End game
        
        # Update Modifiers
        self.update_board_effects()
        
        # Apply Scene Ambient Effects
        if self.scene_manager.current_scene_data:
            self.scene_manager.apply_ambient_effects(minutes)

        # === NEW SYSTEM UPDATES ===

        # Update Condition System (injuries heal/worsen)
        condition_events = self.condition_system.update_time(minutes)
        for event in condition_events:
            if event["type"] == "healed":
                print(f"\n[RECOVERY] Your {event['condition_name']} has healed.")
            elif event["type"] == "worsened":
                print(f"\n[WARNING] Your {event['condition_name']} has worsened!")

        # Update Fracture System state
        self.fracture_system.update_state(
            attention=self.attention_system.attention_level,
            day=self.population_system.current_day,
            in_storm=self.time_system.weather == "storm" if hasattr(self.time_system, 'weather') else False
        )

        # Update archetype based on lens
        lens = self.lens_system.calculate_lens()
        if lens == "believer":
            self.player_archetype = Archetype.BELIEVER
        elif lens == "skeptic":
            self.player_archetype = Archetype.SKEPTIC
        else:
            self.player_archetype = Archetype.NEUTRAL

        # Legacy Recovery / Injury Checks (for backwards compatibility)
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
            
            # Check for Endgame Triggers
            triggered, reason = self.endgame_manager.check_endgame_triggers()
            if triggered:
                print(f"\n{'='*60}")
                print(f"  ENDGAME TRIGGERED: {reason}")
                print(f"{'='*60}\n")
                self.endgame_manager.run_ending_sequence()
                break
            
            # Check for Memory Unlocks
            game_state_for_memory = {
                "skill_system": self.skill_system,
                "player_state": self.player_state,
                "board": self.board,
                "current_scene": self.scene_manager.current_scene_id,
                "event_flags": self.player_state.get("event_flags", set())
            }
            newly_unlocked = self.memory_system.check_memory_triggers(game_state_for_memory)
            for memory_id in newly_unlocked:
                memory = self.memory_system.get_memory(memory_id)
                if memory:
                    # Apply memory effects
                    for stat, value in memory.effects.items():
                        if stat in self.player_state:
                            self.player_state[stat] += value
                            print(f"[{stat.upper()} {'+' if value > 0 else ''}{value}]")
                    
                    # Add to unlocked list
                    self.player_state["suppressed_memories_unlocked"].append(memory_id)
                    
                    # Load memory scene
                    scene_path = self.memory_system.get_memory_scene_path(memory_id)
                    if scene_path and os.path.exists(scene_path):
                        print(f"\n[Press Enter to experience the memory...]")
                        input()
                        # Load and display memory scene
                        with open(scene_path, 'r', encoding='utf-8') as f:
                            import json
                            memory_scene = json.load(f)
                            print("\n" + memory_scene.get("text", ""))
                            print("\n[Press Enter to continue...]")
                            input()
            
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
        lens_str = self.lens_system.calculate_lens().upper()
        attention_display = self.attention_system.get_status_display()
        integration_display = self.integration_system.get_status_display()
        pop_status = f"POP: {self.population_system.population}"
        print(f"TIME: {self.time_system.get_time_string()} | [LENS: {lens_str}] | {pop_status}")
        if attention_display:
            print(f"{attention_display}")
        if integration_display:
            print(f"{integration_display}")
        print(f"SANITY: {san:.0f}% ({san_status}) | REALITY: {real:.0f}% ({real_status})")

        # Show active conditions
        conditions = self.condition_system.get_conditions_summary()
        if conditions:
            cond_names = [c['name'] for c in conditions if c['visible']]
            if cond_names:
                print(f"CONDITIONS: {', '.join(cond_names)}")

        print_separator("=")

        print_boxed_title(scene.get("name", "Unknown Area"))

        if scene.get("background_media"):
            media = scene["background_media"]
            print(f"[MEDIA: Loading {media['type']} '{media['src']}']")

        # === NEW: Use TextComposer for lens-aware text ===
        # Check if scene uses new text structure
        text_data = scene.get("text", {})
        if isinstance(text_data, dict) and "base" in text_data:
            # New format: use TextComposer
            player_state_for_composer = self._get_composer_state()
            result = self.text_composer.compose(text_data, self.player_archetype, player_state_for_composer)
            display_text = result.full_text

            # Apply fractures if triggered
            if result.fracture_applied:
                print("[Something feels wrong...]")
        else:
            # Legacy format: use old lens system
            variants = scene.get("variants", {})
            base_text = text_data if isinstance(text_data, str) else "..."
            display_text = self.lens_system.filter_text(base_text, variants)

        # Apply reality distortion
        display_text = self.apply_reality_distortion(display_text)
        print("\n" + display_text + "\n")

        # === NEW: Passive Clue Detection ===
        passive_clues = scene.get("passive_clues", [])
        if passive_clues:
            player_state_for_clues = self._get_composer_state()
            revealed = self.clue_system.evaluate_passive_clues(passive_clues, player_state_for_clues)
            if revealed:
                print("-" * 40)
                for clue, reveal_text in revealed:
                    print(f"[You notice something...] {reveal_text}")
                print("-" * 40 + "\n")

        # Show NPCs at this location
        location_id = scene.get("location_id")
        if location_id:
            npcs_here = self.npc_system.get_npcs_at_location(location_id)
            if npcs_here:
                npc_names = [f"{npc.name} (Trust: {npc.trust})" for npc in npcs_here]
                print(f"[Present: {', '.join(npc_names)}]")

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
            if clean in ['e', 'evidence', 'board', 'corkboard', 'cb']:
                self.corkboard.run_minigame()
                return "refresh"
            
            # Week 6: Journal Commands
            if clean in ['j', 'journal']:
                self.journal.display_journal()
                return "refresh"
            
            # Taboo Actions (Attention System)
            taboo_map = {
                'whistle': 'whistle_at_aurora',
                'sing': 'sing_outdoors',
                'wave': 'wave_at_lights',
                'photograph': 'photograph_aurora',
                'call': 'call_out',
                'dance': 'dance'
            }
            if clean in taboo_map:
                result = self.attention_system.perform_taboo(taboo_map[clean])
                if result['success']:
                    print(f"\n{result['action_description']}")
                    if result.get('warning'):
                        print(f"[WARNING: {result['warning']}]")
                    if result.get('threshold_crossed'):
                        print("\n*** THE ENTITY IS AWARE OF YOU ***")
                        self.player_state['sanity'] -= 10
                        print("[SANITY -10]")
                        # Trigger integration check
                        self.integration_system.update_from_attention(self.attention_system.attention_level)
                return "refresh"
            
            if clean.startswith('inspect '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    evidence_id = parts[1].strip()
                    self.inspect_evidence(evidence_id)
                else:
                    print("Usage: inspect <evidence_id>")
                return "refresh"
            
            if clean in ['time', 't']:
                print(f"\nCurrent Time: {self.time_system.get_time_string()}")
                date_data = self.time_system.get_date_data()
                print(f"Date: {date_data['date_str']}")
                print(f"Day: {date_data['day_name']}")
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

            # === NEW SYSTEM COMMANDS ===

            # Population Status
            if clean in ['pop', 'population']:
                status = self.population_system.get_status()
                print(f"\n=== KALTVIK POPULATION ===")
                print(f"Current: {status['population']}/{status['starting']} ({status['percentage_lost']:.1f}% lost)")
                print(f"Day: {self.population_system.current_day}")
                if status['events']:
                    print("\nRecent events:")
                    for event in status['events'][-5:]:
                        print(f"  - Day {event['day']}: {event['reason']} ({event['type']}, -{event['count']})")
                return "refresh"

            # View Conditions
            if clean in ['conditions', 'injuries', 'cond']:
                conditions = self.condition_system.get_conditions_summary()
                if not conditions:
                    print("\n[No active conditions]")
                else:
                    print("\n=== ACTIVE CONDITIONS ===")
                    for c in conditions:
                        severity = c.get('severity', 'unknown').upper()
                        treatment_str = f" (Treatable: {', '.join(c.get('available_treatments', []))})" if c.get('available_treatments') else ""
                        print(f"  {c['name']} [{severity}]{treatment_str}")
                        penalties = c.get('penalties', {})
                        if penalties:
                            pen_str = ", ".join([f"{k}:{v:+d}" for k, v in penalties.items()])
                            print(f"    Penalties: {pen_str}")
                return "refresh"

            # Treat Condition
            if clean.startswith('treat '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    condition_name = parts[1].strip()
                    # Find condition by name or ID
                    for cond_id, cond in self.condition_system.active_conditions.items():
                        if cond.name.lower() == condition_name.lower() or cond_id == condition_name:
                            # Try available treatments
                            treatments = self.condition_system.get_available_treatments(cond_id)
                            if not treatments:
                                print(f"No available treatments for {cond.name}")
                            else:
                                # Try first available treatment
                                treatment = treatments[0]
                                result = self.condition_system.apply_treatment(cond_id, treatment)
                                if result.get("success"):
                                    print(f"[TREATMENT] Applied {treatment} to {cond.name}")
                                    if result.get("healed"):
                                        print(f"[HEALED] {cond.name} has been cured!")
                                else:
                                    print(f"[FAILED] {result.get('error', 'Treatment failed')}")
                            break
                    else:
                        print(f"No condition found: {condition_name}")
                else:
                    print("Usage: treat <condition_name>")
                return "refresh"

            # NPC Info
            if clean.startswith('npc '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    npc_name = parts[1].strip().lower()
                    found = False
                    for npc_id, npc in self.npc_system.npcs.items():
                        if npc.name.lower() == npc_name or npc_id == npc_name:
                            print(f"\n=== {npc.name} ===")
                            print(f"Title: {npc.title}")
                            print(f"Trust: {npc.trust}/100")
                            print(f"Fear: {npc.fear}/100")
                            knowledge = self.npc_system.get_available_knowledge(npc_id)
                            if knowledge:
                                print(f"Available Topics: {', '.join(knowledge)}")
                            found = True
                            break
                    if not found:
                        print(f"NPC not found: {npc_name}")
                else:
                    # List all NPCs
                    print("\n=== KNOWN NPCs ===")
                    for npc_id, npc in self.npc_system.npcs.items():
                        print(f"  {npc.name} (Trust: {npc.trust})")
                return "refresh"

            # Debug Mode Commands
            if clean == 'debug':
                self.debug_mode = not self.debug_mode
                print(f"[DEBUG MODE: {'ON' if self.debug_mode else 'OFF'}]")
                return "refresh"
            
            # Theory Resolution Commands
            if clean.startswith('prove '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    theory_id = parts[1].strip()
                    if self.board.resolve_theory(theory_id, True):
                        print(f"[THEORY PROVEN: {theory_id}]")
                    else:
                        print(f"[ERROR: Theory '{theory_id}' not found]")
                return "refresh"
            
            if clean.startswith('disprove '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    theory_id = parts[1].strip()
                    if self.board.resolve_theory(theory_id, False):
                        print(f"[THEORY DISPROVEN: {theory_id}]")
                    else:
                        print(f"[ERROR: Theory '{theory_id}' not found]")
                return "refresh"
            
            if clean.startswith('evidence '):
                parts = raw.split()
                if len(parts) >= 3:
                    theory_id = parts[1]
                    evidence_id = parts[2]
                    if self.board.add_evidence_to_theory(theory_id, evidence_id):
                        print(f"[Evidence linked to theory]")
                    else:
                        print(f"[ERROR: Could not link evidence]")
                else:
                    print("Usage: evidence <theory_id> <evidence_id>")
                return "refresh"
            
            if clean.startswith('talk '):
                parts = raw.split(maxsplit=1)
                if len(parts) > 1:
                    dialogue_id = parts[1].strip()
                    self.start_dialogue(dialogue_id)
                else:
                    print("Usage: talk <dialogue_id>")
                return "refresh"
            
            if clean.startswith('contradict '):
                parts = raw.split()
                if len(parts) >= 3:
                    theory_id = parts[1]
                    evidence_id = parts[2]
                    result = self.board.add_contradiction_to_theory(theory_id, evidence_id)
                    if result.get('success'):
                        print(f"[{result['message']}]")
                        if result.get('sanity_damage', 0) > 0:
                            self.player_state['sanity'] -= result['sanity_damage']
                            print(f"[SANITY -{result['sanity_damage']}]")
                    else:
                        print(f"[ERROR: {result.get('message', 'Could not add contradiction')}]")
                else:
                    print("Usage: contradict <theory_id> <evidence_id>")
                return "refresh"
            
            # Endgame Commands
            if clean in ['submit_report', 'submit']:
                self.player_state["event_flags"].add("submit_report")
                print("[You prepare to submit your final report...]")
                return "refresh"
            
            if clean in ['leave_town', 'leave']:
                self.player_state["event_flags"].add("leave_town")
                print("[You pack your bags and prepare to leave Tyger Tyger...]")
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
                # Standalone LOOK / EXAMINE: Re-display scene
                self.display_scene()
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
        self.event_log.add_event(event_type, **details)

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
        dialogues_dir = resource_path(os.path.join('data', 'dialogues'))
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

    def inspect_evidence(self, evidence_id: str):
        """Display detailed information about a piece of evidence."""
        evidence = self.inventory_system.evidence_collection.get(evidence_id)
        
        if not evidence:
            print(f"\nEvidence '{evidence_id}' not found in collection.")
            return
        
        print("\n" + "="*60)
        print(f"EVIDENCE: {evidence.name}")
        print("="*60)
        print(f"ID: {evidence.id}")
        print(f"Type: {evidence.type}")
        print(f"Description: {evidence.description}")
        print(f"Location Found: {evidence.location}")
        
        if evidence.collected_with:
            print(f"Collected With: {evidence.collected_with}")
        
        if evidence.tags:
            print(f"Tags: {', '.join(evidence.tags)}")
        
        if evidence.related_skills:
            print(f"\nCan be analyzed with: {', '.join(evidence.related_skills)}")
        
        if evidence.analyzed:
            print(f"\n[ANALYZED]")
            for skill, result in evidence.analysis_results.items():
                print(f"  [{skill}] {result}")
        else:
            print(f"\n[NOT YET ANALYZED]")
        
        if evidence.related_npcs:
            print(f"\nRelated NPCs: {', '.join(evidence.related_npcs)}")
        
        print("="*60)

    def show_board(self):
        """Display The Board with visual ASCII art."""
        print(self.board_ui.render())
        print("\nCommands: 'evidence <theory_id> <evidence_id>' | 'contradict <theory_id> <evidence_id>'")
        print("          'prove <theory_id>' | 'disprove <theory_id>'\n")

    def _get_composer_state(self) -> dict:
        """
        Gather player state for TextComposer and ClueSystem.
        Returns dict with skills, flags, theories, equipment, trust, attention.
        """
        # Build skills dict from SkillSystem
        skills = {}
        for skill_name, skill in self.skill_system.skills.items():
            skills[skill_name] = skill.effective_level

        # Build equipment list from inventory
        inventory_items = []
        equipped_items = []
        if hasattr(self.inventory_system, 'inventory'):
            for item in self.inventory_system.inventory:
                inventory_items.append(item.id if hasattr(item, 'id') else str(item))
        if hasattr(self.inventory_system, 'equipped'):
            for item in self.inventory_system.equipped:
                equipped_items.append(item.id if hasattr(item, 'id') else str(item))

        # Build flags dict from player_state event_flags
        flags = {}
        event_flags = self.player_state.get("event_flags", set())
        for flag in event_flags:
            flags[flag] = True

        # Get active theories from Board
        active_theories = []
        if hasattr(self.board, 'get_active_theories'):
            active_theories = self.board.get_active_theories()
        elif hasattr(self.board, 'theories'):
            for theory_id, theory in self.board.theories.items():
                if hasattr(theory, 'status') and theory.status in ['active', 'internalizing']:
                    active_theories.append(theory_id)

        # Build trust dict from NPC system
        trust = {}
        for npc_id, npc in self.npc_system.npcs.items():
            trust[npc_id] = npc.trust

        return {
            "skills": skills,
            "flags": flags,
            "active_theories": active_theories,
            "inventory": inventory_items,
            "equipped": equipped_items,
            "trust": trust,
            "attention": self.attention_system.attention_level,
            "reality": self.player_state.get("reality", 100),
            "sanity": self.player_state.get("sanity", 100),
            "archetype": self.player_archetype.value if self.player_archetype else "neutral"
        }

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
