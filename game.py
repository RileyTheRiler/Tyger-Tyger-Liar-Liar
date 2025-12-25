
import sys
import os
import time
import random

# Ensure src and its subdirectories are in path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    return path

# Add subdirectories to path for legacy flat-import compatibility
sys.path.append(resource_path('src'))
sys.path.append(resource_path('src/engine'))
sys.path.append(resource_path('src/ui'))
sys.path.append(resource_path('src/content'))

from mechanics import SkillSystem, CharacterSheetUI
from board import Board
from ui.board_ui import BoardUI
from lens_system import LensSystem
from attention_system import AttentionSystem
from integration_system import IntegrationSystem
from time_system import TimeSystem
from endgame_manager import EndgameManager
from memory_system import MemorySystem
from scene_manager import SceneManager
from input_system import CommandParser, InputMode
from content.dialogue_manager import DialogueManager
from combat import CombatManager
from corkboard_minigame import CorkboardMinigame
from autopsy_system import AutopsyMinigame
from engine.flashback_system import FlashbackManager
from ui.io_system import OutputBuffer
from inventory_system import InventoryManager, Item, Evidence
from save_system import EventLog, SaveSystem
from journal_system import JournalManager
from ui.interface import print_separator, print_boxed_title, print_numbered_list, format_skill_result, Colors
from engine.text_composer import TextComposer, Archetype
from location_system import LocationManager
from trigger_system import TriggerManager
from liar_engine import LiarEngine
from population_system import PopulationSystem
from engine.injury_system import InjurySystem
from engine.trauma_system import TraumaSystem
from engine.chase_system import ChaseSystem
from engine.environmental_effects import EnvironmentalEffects
from engine.psychological_system import PsychologicalState
from engine.fear_system import FearManager
from engine.unreliable_narrator import HallucinationEngine
from npc_system import NPCSystem


class Game:
    def __init__(self):
        # Initialize Output Buffer
        self.output = OutputBuffer()

        # Load Config
        import json
        with open(resource_path('game.config.json'), 'r') as f:
            self.config = json.load(f)

        # Player State
        self.player_state = {
            "sanity": 100.0,
            "reality": 100.0,
            "archetype": Archetype.NEUTRAL,
            "resonance_count": 347,
            "thermal_mode": False,
            "inventory": [],
            "thoughts": [],
            "injuries": [],
            "moral_corruption_score": 0,
            "critical_choices": [],
            "suppressed_memories_unlocked": [],
            "event_flags": set(),
            "playtime_minutes": 0,
            "failed_reds": [],
            "checked_whites": [],
            
            # Psychological State (Week 15)
            "mental_load": 0,
            "fear_level": 0,
            "disorientation": False,
            "instability": False,
            "hallucination_history": [],
            
            # Location System (Week 7)
            "current_location": "trailhead",
            "location_states": {},
            "discovered_locations": {"trailhead"},
            "fired_triggers": set()
        }

        # Audio State
        self.current_music = None
        self.sfx_queue = []

        # Initialize Systems
        self.time_system = TimeSystem()
        self.board = Board()
        self.board_ui = BoardUI(self.board)
        self.skill_system = SkillSystem(resource_path(os.path.join('data', 'skills.json')))
        self.lens_system = LensSystem(self.skill_system, self.board)
        self.attention_system = AttentionSystem()
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
        
        # Initialize Text Composer (Replaces LensSystem eventually)
        self.text_composer = TextComposer(self.skill_system, self.board, self.player_state)

        # Initialize Flashback Manager (Phase 6)
        self.flashback_manager = FlashbackManager(self.skill_system, self.player_state)

        # Initialize Scene Manager
        self.scene_manager = SceneManager(
            self.time_system, 
            self.board, 
            self.skill_system, 
            self.player_state,
            self.flashback_manager
        )
        self.last_composed_text = ""
        
        # Initialize Population & Liar Engine
        self.population_system = PopulationSystem()
        self.liar_engine = LiarEngine(self.skill_system, self.inventory_system)
        
        # Initialize NPC System (Week 11)
        npcs_dir = resource_path(os.path.join('data', 'npcs'))
        self.npc_system = NPCSystem(npcs_dir if os.path.exists(npcs_dir) else None)
        
        # Initialize Dialogue Manager
        self.dialogue_manager = DialogueManager(
            self.skill_system,
            self.board,
            self.player_state,
            self.npc_system  # Week 11: Pass NPC system
        )
        self.in_dialogue = False
        
        # Initialize Endgame and Memory Systems
        self.endgame_manager = EndgameManager(self.board, self.player_state, self.skill_system)
        self.memory_system = MemorySystem(resource_path(os.path.join('data', 'memories', 'memories.json')))
        
        # Initialize Week 13 Systems: Injury, Trauma, Chase, Environmental
        self.injury_system = InjurySystem()
        self.injury_system.load_injury_database(resource_path(os.path.join('data', 'injuries.json')))
        
        self.trauma_system = TraumaSystem()
        self.trauma_system.load_trauma_database(resource_path(os.path.join('data', 'trauma_types.json')))
        
        self.chase_system = ChaseSystem()
        self.chase_system.load_chase_scenarios(resource_path(os.path.join('data', 'chase_scenarios.json')))
        
        self.environmental_effects = EnvironmentalEffects()
        # Apply environmental modifiers to skill system
        self.environmental_effects.apply_to_skill_system(self.skill_system)
        
        # Initialize Combat Manager with new systems
        self.combat_manager = CombatManager(
            self.skill_system, 
            self.player_state,
            injury_system=self.injury_system,
            trauma_system=self.trauma_system,
            inventory_system=self.inventory_system
        )
        self.combat_manager.load_encounter_templates(resource_path(os.path.join('data', 'encounters.json')))
        
        # Initialize Journal Manager (Week 6)
        self.journal = JournalManager()
        
        # Initialize Location and Trigger Systems (Week 7)
        self.location_manager = LocationManager()
        self.location_manager.load_locations(resource_path(os.path.join('data', 'locations.json')))
        self.player_state["location_states"] = self.location_manager.initialize_states()
        
        self.trigger_manager = TriggerManager()
        self.trigger_manager.load_triggers(resource_path(os.path.join('data', 'triggers.json')))
        
        # Initialize Psychological Systems (Week 15)
        self.psych_state = PsychologicalState(self.player_state)
        
        self.fear_manager = FearManager()
        fear_events_path = resource_path(os.path.join('data', 'fear_events'))
        self.fear_manager.load_fear_events(fear_events_path)
        
        self.hallucination_engine = HallucinationEngine()
        hallucinations_path = resource_path(os.path.join('data', 'hallucinations'))
        self.hallucination_engine.load_hallucination_templates(hallucinations_path)
        
        self.active_argument = None # Phase 4 internal debates
        self.active_argument = None # Phase 4 internal debates
        self.current_autopsy = None # Phase 5 autopsies
        
        # Load Documents (Phase 6)
        docs_path = resource_path(os.path.join('data', 'documents', 'documents.json'))
        self.inventory_system.load_documents(docs_path)
        
        # Load Scenes
        scenes_dir = resource_path(os.path.join('data', 'scenes'))
        root_scenes = resource_path('scenes.json')
        self.scene_manager.load_scenes_from_directory(scenes_dir, root_scenes)

    
    def print(self, text=""):
        self.output.print(str(text))

    def on_time_passed(self, minutes: int):
        msgs = self.board.on_time_passed(minutes)
        if msgs:
            self.print("\n*** BOARD UPDATE ***")
            for m in msgs:
                self.print(f" -> {m}")
            self.print("********************\n")
        
        # Attention decay
        hours = minutes / 60.0
        self.attention_system.decay_attention(hours)
        
        # Evidence aging (Phase 5)
        self.inventory_system.update_evidence_aging(hours)
        
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
                self.print(f"\n*** INTEGRATION STAGE {result['stage']}: {result['name']} ***")
                self.print(f"{result['description']}")
                if result.get('game_over'):
                    self.print("\n=== GAME OVER: INTEGRATED ===\n")
                    return  # End game
        
        # Week 7: Check Triggers after time pass
        triggered_events = self.trigger_manager.check_triggers(self.get_game_state())
        for event in triggered_events:
            self.apply_trigger_effects(event)
        
        # Week 15: Psychological Systems
        # Fear Level decay
        fear_decay_result = self.psych_state.decay_fear(minutes)
        for msg in fear_decay_result.get("messages", []):
            self.print(msg)
        
        # Check for fear events
        fear_game_state = self.get_game_state()
        fear_game_state["attention_level"] = self.attention_system.attention_level
        fear_game_state["location_data"] = self.location_manager.get_location(
            self.player_state.get("current_location", "")
        )
        
        triggered_fears = self.fear_manager.check_fear_triggers(fear_game_state)
        for fear_event in triggered_fears:
            self.print(f"\n{Colors.RED}*** {fear_event.get('event_name', 'FEAR EVENT')} ***{Colors.RESET}")
            self.print(fear_event.get("text_overlay", ""))
            
            # Apply fear effects
            if "fear_level" in fear_event:
                fear_result = self.psych_state.add_fear(
                    fear_event["fear_level"],
                    fear_event.get("event_name", "Unknown")
                )
                for msg in fear_result.get("messages", []):
                    self.print(msg)
            
            if "sanity" in fear_event:
                sanity_result = self.psych_state.modify_sanity(
                    fear_event["sanity"],
                    fear_event.get("event_name", "Fear")
                )
                for msg in sanity_result.get("messages", []):
                    self.print(msg)
            
            if "mental_load" in fear_event:
                load_result = self.psych_state.add_mental_load(
                    fear_event["mental_load"],
                    fear_event.get("event_name", "Fear")
                )
                for msg in load_result.get("messages", []):
                    self.print(msg)
            
            # Queue audio if specified
            if "audio_cue" in fear_event:
                self.sfx_queue.append(fear_event["audio_cue"])
        
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
            self.print(f"\n[RECOVERY] Your '{h['name']}' has healed properly.")
            # Restore stats if needed?

    def modify_resonance(self, amount: int, cause: str = "Unknown"):
        """Modify the global population resonance counter."""
        old_val = self.player_state["resonance_count"]
        self.player_state["resonance_count"] += amount
        new_val = self.player_state["resonance_count"]
        
        diff = new_val - old_val
        if diff != 0:
            color = Colors.RED if amount < 0 else Colors.CYAN
            self.print(f"\n[{color}RESONANCE SHIFT: {old_val} -> {new_val} ({cause}){Colors.RESET}]")
            
            # Sync with PopulationSystem
            if amount < 0:
                self.population_system.record_death(cause, count=abs(amount))
            elif amount > 0:
                self.population_system.record_correction(cause, new_val)
                
            self.check_resonance_event(diff)

    def check_resonance_event(self, diff: int):
        """Trigger Entity reactions based on population shifts."""
        current = self.player_state["resonance_count"]
        
        # Logic Check
        # If population drops (death), Entity gets excited/agitated
        if diff < 0:
            check = self.skill_system.roll_check("Paranormal Sensitivity", 12, "hidden", check_id=f"res_shift_{current}")
            if check["success"]:
                 self.print("\n[PARANORMAL SENSITIVITY] The static in the air thickens. Something is feeding.")
            else:
                 self.print("\n[INTUITION] The town feels... emptier than it should.")
                 
            # Sanity Hit if significant
            if abs(diff) > 1:
                self.player_state["sanity"] -= 5
                self.print("[SANITY -5] The loss reverberates.")

        # If population rises (Arrival?), Entity might be curious
        elif diff > 0:
             self.print("\n[LOGIC] New variables entered the system.")


    def update_board_effects(self):
        # Clear old Board modifiers (hacky reset for now)
        for skill in self.skill_system.skills.values():
            skill.set_modifier("Board", 0)
            
        current_mods = self.board.get_all_modifiers()
        for skill_name, val in current_mods.items():
            skill = self.skill_system.get_skill(skill_name)
            if skill:
                skill.set_modifier("Board", val)

    def get_game_state(self):
        """Package current game state for trigger evaluation and movement checks."""
        return {
            "current_location": self.player_state.get("current_location"),
            "location_states": self.player_state.get("location_states", {}),
            "player_flags": self.player_state.get("event_flags", set()),
            "time": self.time_system.current_time,
            "board": self.board,
            "skill_system": self.skill_system,
            "sanity": self.player_state["sanity"],
            "reality": self.player_state["reality"]
        }

    def apply_trigger_effects(self, trigger):
        """Apply the effects of a fired trigger."""
        effects = trigger.get("effects", {})
        self.print(f"\n*** EVENT: {trigger.get('id', 'Mysterious Occurrence')} ***")
        
        # Stat modifications
        self.apply_effects(effects)
        
        # Player Flags
        for flag in effects.get("set_player_flags", []):
            self.player_state["event_flags"].add(flag)
            
        # Location Flags
        loc_flags = effects.get("set_location_flags", {})
        cur_loc = self.player_state.get("current_location")
        if loc_flags and cur_loc:
            for flag, val in loc_flags.items():
                self.player_state["location_states"][cur_loc][flag] = val
        
        # Scene transition
        if "scene" in effects:
            scene_id = effects["scene"]
            new_scene = self.scene_manager.load_scene(scene_id)
            if new_scene:
                self.print(f"\n[Something pulled you to a new perspective...]")
                # We don't return here because we want other effects to finish
                # The main loop will display the new scene

    def go_to_location(self, target_id):
        """Move the player to a new location."""
        current = self.player_state.get("current_location")
        loc = self.location_manager.get_location(target_id)
        
        if not loc:
            self.print(f"I don't know how to get to '{target_id}'.")
            return
            
        # Connection check
        connections = self.location_manager.get_connected_locations(current)
        if target_id not in connections:
            self.print(f"You can't get to {loc['name']} from here.")
            return
            
        # Access condition check
        if not self.location_manager.can_enter(target_id, self.get_game_state()):
            self.print(f"The way to {loc['name']} is blocked or you aren't ready yet.")
            return
            
        # Move
        travel_time = connections[target_id].get("travel_minutes", 10)
        self.print(f"\nYou head towards {loc['name']} ({travel_time} minutes)...")
        self.time_system.advance_time(travel_time)
        
        self.player_state["current_location"] = target_id
        self.player_state["discovered_locations"].add(target_id)
        
        # Trigger entry scene
        entry_scene = loc.get("on_enter_scene")
        if entry_scene:
            new_scene = self.scene_manager.load_scene(entry_scene)
            if new_scene:
                self.print(f"\n[Arrived at {loc['name']}]")

    def display_map(self):
        """Show discovered locations and their connections."""
        current = self.player_state.get("current_location")
        discovered = self.player_state.get("discovered_locations", set())
        
        self.print("\n=== KNOWN LOCATIONS ===")
        for loc_id in discovered:
            loc = self.location_manager.get_location(loc_id)
            if not loc: continue
            
            marker = " [YOU ARE HERE]" if loc_id == current else ""
            self.print(f"  • {loc['name']}{marker}")
            
            # Show connections
            connections = self.location_manager.get_connected_locations(loc_id)
            for conn_id, data in connections.items():
                if conn_id in discovered:
                    accessible = self.location_manager.can_enter(conn_id, self.get_game_state())
                    status = "" if accessible else " (BLOCKED)"
                    travel_time = data.get("travel_minutes", 0)
                    self.print(f"    → {self.location_manager.get_location(conn_id)['name']} ({travel_time}min){status}")

    def display_current_location(self):
        """Show current location details."""
        loc_id = self.player_state.get("current_location")
        loc = self.location_manager.get_location(loc_id)
        if not loc:
            self.print("You are adrift in the void.")
            return
            
        self.print(f"\n📍 Current Location: {loc['name']}")
        self.print(f"   {loc['description']}")
        
        state = self.player_state["location_states"].get(loc_id, {})
        if state.get("searched"):
            self.print("   [This area has been thoroughly searched]")
        if state.get("locked"):
            self.print("   [Locked]")

    def search_location(self):
        """Search current location with passive skill checks."""
        loc_id = self.player_state.get("current_location")
        loc = self.location_manager.get_location(loc_id)
        
        state = self.player_state["location_states"].get(loc_id, {})
        if state.get("searched"):
            self.print("You've already searched this area thoroughly.")
            return
            
        self.print(f"\nYou carefully search {loc['name']}...")
        self.time_system.advance_time(15)  # Searching takes time
        
        # Passive checks for the location
        # (Assuming location data might have search_checks in the future)
        # For now, let's mark it searched
        self.player_state["location_states"][loc_id]["searched"] = True
        self.print("\n[Location marked as searched]")

    def start_game(self, start_scene_id="bedroom"):
        self.output.clear()
        
        # Initial Load
        scene = self.scene_manager.load_scene(start_scene_id)
        if not scene:
            # Fallback if specific scene not found
            scene = self.scene_manager.load_scene("arrival_bus")
            start_scene_id = "arrival_bus"

        if not scene:
            self.print(f"Failed to load initial scene '{start_scene_id}'.")
            return self.output.flush()
        
        # Log initial scene entry
        self.log_event("scene_entry", scene_id=start_scene_id, scene_name=scene.get("name", "Unknown"))
        
        # Initial Music
        if "music" in scene:
            self.current_music = scene["music"]
        
        self.display_state()
        return self.output.flush()

    def step(self, user_input):
        self.output.clear()
        
        # 1. Process Input
        if self.in_dialogue:
             self.process_dialogue_input(user_input)
        else:
             choices = self.scene_manager.current_scene_data.get("choices", [])
             action_result = self.process_command(user_input, choices)
             
             if action_result == "quit":
                 return "QUIT"
                 
             if isinstance(action_result, dict):
                 # Check for dialogue trigger
                 if "type" in action_result and action_result["type"] == "dialogue":
                     dialogue_id = action_result.get("dialogue_id")
                     if dialogue_id:
                         self.start_dialogue(dialogue_id)
                 else:
                     # Transitions
                     next_id = self.process_choice(action_result)
                     if next_id:
                          # Load next scene
                          new_scene = self.scene_manager.load_scene(next_id)
                          if not new_scene:
                              self.print(f"Cannot move to {next_id} (Locked or Missing).")
                          else:
                          # Log scene entry
                              self.log_event("scene_entry", scene_id=next_id, scene_name=new_scene.get("name", "Unknown"))
                              
                              # Update Music if scene defines it
                              if "music" in new_scene:
                                  self.current_music = new_scene["music"]

        # 2. Run Passive Mechanics (Checks that happen every tick/update)
        # Note: Time advancement usually happens via specific actions (travel, wait), 
        # so we don't auto-advance time here unless we want real-time (no).
        triggered_endgame = self.run_passive_mechanics()
        
        if triggered_endgame:
            pass # The mechanics printed the ending, we just stop? 
            # Ideally step returns a status code
            
        # 3. Display Updated State
        if not triggered_endgame:
            self.display_state()
            
        return self.output.flush()

    def get_ui_state(self):
        """Return structured state for the UI frontend."""
        scene = self.scene_manager.current_scene_data or {}
        # Filter choices validation if needed, or just send raw
        # Capture SFX queue before clearing
        sfx_to_play = list(self.sfx_queue)
        self.sfx_queue.clear() # Clear transient queue

        return {
            "sanity": self.player_state.get("sanity", 100),
            "reality": self.player_state.get("reality", 100),
            "time": self.time_system.get_time_string(),
            "location": scene.get("name", "Unknown"),
            "inventory": [i.name for i in self.inventory_system.carried_items],
            "passive_interrupts": self.skill_system.check_passive_interrupts(
                self.last_composed_text,
                self.player_state["sanity"]
            ),
            "population_status": self.population_system.get_population_status(),
            "theories_active": self.board.get_active_or_internalizing_count(),
            "input_mode": self.input_mode.name if hasattr(self.input_mode, 'name') else str(self.input_mode),
            "choices": scene.get("choices", []),
            "board_data": self.board.get_board_data(),
            "music": self.current_music,
            "sfx_queue": sfx_to_play
        }

    def run_passive_mechanics(self):
        # 1. Endgame Triggers
        triggered, reason = self.endgame_manager.check_endgame_triggers()
        if triggered:
            self.print(f"\n{'='*60}")
            self.print(f"  ENDGAME TRIGGERED: {reason}")
            self.print(f"{'='*60}\n")
            self.endgame_manager.run_ending_sequence(printer=self.print)
            return True
        
        # 2. Memory Unlocks
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
                        self.print(f"[{stat.upper()} {'+' if value > 0 else ''}{value}]")
                
                # Add to unlocked list
                self.player_state["suppressed_memories_unlocked"].append(memory_id)
                
                # Load memory scene (Simply print it for now, blocking waiting is hard in API)
                scene_path = self.memory_system.get_memory_scene_path(memory_id)
                if scene_path and os.path.exists(scene_path):
                    with open(scene_path, 'r', encoding='utf-8') as f:
                        import json
                        memory_scene = json.load(f)
                        self.print("\n" + memory_scene.get("text", ""))
        
        # 3. Breakdowns
        if self.player_state["sanity"] <= 0:
            self.print("\n>> SANITY CRITICAL: You collapse under the weight of your own mind. <<")
            self.player_state["sanity"] = 10 
            self.log_event("breakdown", breakdown_type="sanity")

        if self.player_state["reality"] <= 0:
            self.print("\n>> REALITY FRACTURE: The world dissolves. Who are you? <<")
            self.player_state["reality"] = 10
            self.log_event("breakdown", breakdown_type="reality")
            
        return False

    def display_state(self):
        if self.in_dialogue:
            self.display_dialogue()
        else:
            self.display_scene()
            
            choices = self.scene_manager.current_scene_data.get("choices", [])
            
            interrupts = self.skill_system.check_passive_interrupts(
                self.last_composed_text,
                self.player_state["sanity"]
            )
            if interrupts:
                self.print("\n" + "~" * 60)
                for item in interrupts:
                    if isinstance(item, dict):
                        # Format structured interrupt
                        skill = item['skill']
                        text = item['text']
                        # Simple color simulation for CLI text if supported or just text
                        self.print(f" [{skill}] {text}")
                    else:
                        self.print(f" {item}")
                self.print("~" * 60)

            self.display_status_line()
            self.display_choices(choices)

    def display_status_line(self):
        mode_str = "DIALOGUE" if self.input_mode == InputMode.DIALOGUE else "INVESTIGATION"
        debug_str = " [DEBUG]" if self.debug_mode else ""
        print_separator("-", 64, printer=self.print)
        self.print(f"[{mode_str} MODE{debug_str}] - (b)oard, (c)haracter, (i)nventory, (e)vidence")
        self.print("                   (w)ait, (s)leep, (h)elp, (q)uit, [switch]")
        print_separator("-", 64, printer=self.print)

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
        # Level 2 Distortion (25-50): Word jumbling and subtle corruption
        if reality < 50:
            words = text.split()
            new_words = []
            for word in words:
                if random.random() < 0.1: # 10% chance to corrupt word
                    if random.random() < 0.5:
                        # Jumble
                        w_list = list(word)
                        random.shuffle(w_list)
                        new_words.append("".join(w_list))
                    else:
                        # Corrupt with static
                        noise = ["▓", "▒", "░", "█"]
                        new_words.append(random.choice(noise) * len(word))
                else:
                    new_words.append(word)
            text = " ".join(new_words)

        # Level 3 Distortion (<25): Hallucinated sentences, redacting blocks, and reversals
        if reality < 25:
            if random.random() < 0.5:
                hallucinations = [
                    "\nTHEY ARE WATCHING YOU.",
                    "\nIT IS INSIDE THE WALLS.",
                    "\nDON'T TRUST THE MIRROR.",
                    "\nYOU ARE NOT ALONE.",
                    "\nTHE BLUE FLUID IS HUNGRY."
                ]
                text += f"\n{Colors.RED}{random.choice(hallucinations)}{Colors.RESET}"
            
            # Block redaction
            if random.random() < 0.3:
                 paragraphs = text.split("\n\n")
                 if paragraphs:
                     idx = random.randint(0, len(paragraphs)-1)
                     paragraphs[idx] = "█" * len(paragraphs[idx])
                     text = "\n\n".join(paragraphs)
                     
        # Sanity effects (different from reality)
        sanity = self.player_state.get("sanity", 100.0)
        if sanity < 20:
            # Randomly reverse a sentence
            if random.random() < 0.4:
                sentences = text.split(". ")
                if sentences:
                    idx = random.randint(0, len(sentences)-1)
                    sentences[idx] = sentences[idx][::-1]
                    text = ". ".join(sentences)
        
        return text

    def display_scene(self):
        scene = self.scene_manager.current_scene_data
        self.print("\n" + "="*60)
        
        # HUD
        san = self.player_state["sanity"]
        real = self.player_state["reality"]
        san_status = "STABLE" if san >= 75 else "UNSETTLED" if san >= 50 else "HYSTERIA" if san >= 25 else "PSYCHOSIS"
        real_status = "LUCID" if real >= 75 else "DOUBT" if real >= 50 else "DELUSION" if real >= 25 else "BROKEN"

        print_separator("=", color=Colors.CYAN, printer=self.print)
        # Lens system calculates based on current skill/board state automatically
        print_separator("=", printer=self.print)
        lens_str = self.lens_system.calculate_lens().upper()
        attention_display = self.attention_system.get_status_display()
        integration_display = self.integration_system.get_status_display()

        # Colorize Status
        san_color = Colors.GREEN if san > 50 else Colors.YELLOW if san > 25 else Colors.RED
        real_color = Colors.MAGENTA if real > 50 else Colors.YELLOW if real > 25 else Colors.RED

        self.print(f"{Colors.BOLD}TIME: {self.time_system.get_time_string()}{Colors.RESET} | [LENS: {Colors.CYAN}{lens_str}{Colors.RESET}]")
        if attention_display:
            self.print(f"{Colors.RED}{attention_display}{Colors.RESET}")
        if integration_display:
            self.print(f"{Colors.MAGENTA}{integration_display}{Colors.RESET}")
        self.print(f"SANITY: {san_color}{san:.0f}% ({san_status}){Colors.RESET} | REALITY: {real_color}{real:.0f}% ({real_status}){Colors.RESET}")
        print_separator("=", color=Colors.CYAN, printer=self.print)
        
        print_boxed_title(scene.get("name", "Unknown Area"), printer=self.print)
        
        if scene.get("background_media"):
            media = scene["background_media"]
            self.print(f"[MEDIA: Loading {media['type']} '{media['src']}']")
        
        # Text Composition Logic
        # 1. Determine Archetype from Lens System
        current_lens = self.lens_system.calculate_lens()
        archetype_map = {
            "believer": Archetype.BELIEVER,
            "skeptic": Archetype.SKEPTIC,
            "haunted": Archetype.HAUNTED
        }
        archetype = archetype_map.get(current_lens, Archetype.NEUTRAL)
        
        # Override if manually set in player_state
        if self.player_state.get("archetype", Archetype.NEUTRAL) != Archetype.NEUTRAL:
             archetype = self.player_state["archetype"]

        # 2. Prepare Data for Composer (Adapter Layer)
        text_obj = scene.get("text", {"base": "..."})
        if isinstance(text_obj, str):
            text_data = {
                "base": text_obj,
                "lens": scene.get("variants", {}),
                "inserts": scene.get("inserts", [])
            }
        else:
            text_data = text_obj

        # 3. Compose
        thermal_active = self.player_state.get("thermal_mode", False)
        composed_result = self.text_composer.compose(text_data, archetype, self.player_state, thermal_mode=thermal_active)
        self.last_composed_text = self.apply_reality_distortion(composed_result.full_text)
        self.print("\n" + self.last_composed_text + "\n")
        
        # Check for Contradictions (Liar Engine)
        liar_interrupts = self.liar_engine.check_contradictions(self.last_composed_text)
        if liar_interrupts:
            for interrupt in liar_interrupts:
                 self.print(f" [{Colors.PURPLE}{interrupt['skill']}{Colors.RESET}] {interrupt['text']}")
                 # Update reputation for Skepticism successfully finding a lie
                 self.skill_system.update_skill_reputation("Skepticism", True)
        
        # General Passive Interrupts (Phase 4)
        sanity = self.player_state.get("sanity", 100.0)
        curr_time = (self.time_system.current_time - self.time_system.start_time).total_seconds() / 60.0
        
        
        interrupts = self.skill_system.check_passive_interrupts(self.last_composed_text, sanity, curr_time)
        
        # Theory Commentary Pass
        active_tids = [t.id for t in self.board.theories.values() if t.status == "active"]
        theory_interjections = self.skill_system.check_theory_commentary(active_tids)
        for ti in theory_interjections:
            # Inject theory commentary with a chance proportional to its relevance or mental strain
            if random.random() < 0.7: # 70% chance to show active theory thought
                interrupts.append(ti)
        
        for inter in interrupts:
            if inter.get("type") == "argument":
                self.active_argument = inter
                self.print(f"\n{Colors.BOLD}{Colors.RED}!!! INTERNAL DEBATE !!!{Colors.RESET}")
                s1, s2 = inter["skills"]
                self.print(f"[{s1['skill']}] vs [{s2['skill']}]")
                self.print(f" {s1['skill']}: {s1['text']}")
                self.print(f" {s2['skill']}: {s2['text']}")
                self.print(f" Choose a perspective: {Colors.CYAN}'side {s1['skill'].lower()}'{Colors.RESET} or {Colors.CYAN}'side {s2['skill'].lower()}'{Colors.RESET}")
            else:
                self.print(f" [{Colors.YELLOW}{inter['skill']}{Colors.RESET}] {inter['text']}")
        
        if "ambient_effects" in scene:
            amb = scene["ambient_effects"]
            if amb.get("sanity_drain_per_min", 0) > 0:
                self.print("* The atmosphere is oppressive. *")

        # 4. Thermal Objects Check (Phase 5)
        if thermal_active:
             self.check_thermal_signatures(scene)

    def check_thermal_signatures(self, scene_data):
        """
        Check for objects with abnormal temperatures in the scene.
        Triggers passive Medicine/Logic checks.
        """
        objects = scene_data.get("objects", {})
        for obj_name, obj_data in objects.items():
            # Assume objects might have 'temperature' key directly or in properties
            temp = obj_data.get("temperature", 70.0)
            
            # Hot Check
            if temp > 99.1:
                # Medicine Check
                check = self.skill_system.roll_check("Medicine", 10, "hidden", check_id=f"thermal_hot_{obj_name}_{temp}")
                if check["success"]:
                    status = "overclocked" if temp > 101 else "feverish"
                    msg = {
                        "skill": "MEDICINE",
                        "text": f"Object '{obj_name}' is {temp}°F. It doesn't look sick; it looks... {status}.",
                        "color": "blue", # Reason color
                        "icon": "medicine"
                    }
                    self.print(f" [MEDICINE] {msg['text']}")

            # Cold Check
            elif temp < 32.0:
                 check = self.skill_system.roll_check("Logic", 10, "hidden", check_id=f"thermal_cold_{obj_name}_{temp}")
                 if check["success"]:
                    msg = {
                        "skill": "LOGIC",
                        "text": f"Object '{obj_name}' is {temp}°F. Entropy is being reversed here.",
                        "color": "blue",
                        "icon": "logic"
                    }
                    self.print(f" [LOGIC] {msg['text']}")

    def display_choices(self, choices):
        # Week 7: Show current location context
        self.display_current_location()

        # List Choices (Dialogue Mode or Hybrid)
        if choices:
            print_numbered_list("CHOICES", choices, printer=self.print)
        
        # List Connected Scenes (Spatial Movement innerhalb des Ortes)
        connected = self.scene_manager.get_available_scenes()
        offset = len(choices)
        if connected and self.input_mode == InputMode.INVESTIGATION:
            paths = []
            for route in connected:
                status = "" if route["accessible"] else "(BLOCKED)"
                paths.append(f"Go to {route['name']} {status}")
            if paths:
                print_numbered_list("LOCAL PATHS", paths, offset=offset, printer=self.print)
                offset += len(paths)

        # List Connected Locations (World Navigation)
        if self.input_mode == InputMode.INVESTIGATION:
            cur_loc = self.player_state.get("current_location")
            loc_connections = self.location_manager.get_connected_locations(cur_loc)
            world_paths = []
            self.location_choice_map = {} # Map index to location ID
            
            for loc_id, data in loc_connections.items():
                loc = self.location_manager.get_location(loc_id)
                if not loc: continue
                
                accessible = self.location_manager.can_enter(loc_id, self.get_game_state())
                status = "" if accessible else " (LOCKED/HIDDEN)"
                travel_time = data.get("travel_minutes", 10)
                
                # Show only discovered locations or explicitly marked visible ones?
                # For now, show all immediate neighbors
                world_paths.append(f"Travel to {loc['name']} ({travel_time}m){status}")
                self.location_choice_map[offset + len(world_paths)] = loc_id
                
            if world_paths:
                print_numbered_list("TRAVEL", world_paths, offset=offset, printer=self.print)

    def process_command(self, raw_input, choices):
        raw = raw_input.strip()
        if not raw:
            return "refresh"
        
        # Handle special commands first
        clean = raw.lower()
        if clean in ['q', 'quit', 'exit']:
            return "quit"
        if clean in ['b', 'board']:
            self.show_board()
            return "refresh"
        if clean in ['c', 'character', 'sheet']:
            self.char_ui.display() # This prints directly, need to check it
            return "refresh"
        if clean in ['switch', 'swap']:
            self.toggle_mode()
            return "refresh"
        if clean in ['thermal', 'toggle_thermal']:
            self.toggle_thermal()
            return "refresh"
        if clean in ['h', 'help', '?']:
            self.handle_parser_command("HELP", None)
            return "refresh"
        
        # Inventory & Evidence Commands
        if clean in ['i', 'inventory', 'inv']:
            self.inventory_system.list_inventory() # This prints directly
            return "refresh"
        if clean in ['e', 'evidence', 'board', 'corkboard', 'cb']:
            self.corkboard.run_minigame() # This has input() loops! Danger.
            # TODO: Disable corkboard minigame for now or refactor
            self.print("[Corkboard Minigame not supported in API mode yet]")
            # self.corkboard.run_minigame()
            return "refresh"
        
        # Week 6: Journal Commands
        if clean in ['j', 'journal']:
            self.journal.display_journal() # Prints directly
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
                self.print(f"\n{result['action_description']}")
                if result.get('warning'):
                    self.print(f"[WARNING: {result['warning']}]")
                if result.get('threshold_crossed'):
                    self.print("\n*** THE ENTITY IS AWARE OF YOU ***")
                    self.player_state['sanity'] -= 10
                    self.print("[SANITY -10]")
                    # Trigger integration check
                    self.integration_system.update_from_attention(self.attention_system.attention_level)
            return "refresh"
        
        # Phase 4 Commands
        if clean.startswith('side '):
            if not self.active_argument:
                self.print("There is no active internal debate to resolve.")
                return "refresh"
            
            choice = clean.replace('side ', '').strip().upper()
            # Skill names in the argument are uppercase keys in the dictionaries
            skill_options = [s['skill'] for s in self.active_argument['skills']]
            
            if choice in skill_options:
                rejected = [s for s in skill_options if s != choice][0]
                self.skill_system.resolve_argument(choice, rejected)
                self.print(f"\n[You have sided with {choice}.]")
                self.print(f" {choice} feels emboldened (+2). {rejected} is shaken (-1).")
                self.active_argument = None
                return "refresh"
            else:
                self.print(f"Choose one of the debating skills: {', '.join(skill_options)}")
                return "refresh"

        if clean.startswith('suppress '):
            skill_name = clean.replace('suppress ', '').strip().title()
            curr_minutes = (self.time_system.current_time - self.time_system.start_time).total_seconds() / 60.0
            
            if self.skill_system.suppress_skill(skill_name, 120, curr_minutes): # 2 hours
                self.player_state['sanity'] -= 5
                self.print(f"\n[You have suppressed {skill_name} for 2 hours.]")
                self.print(f" Your mind is quieter, but the effort is draining. (-5 Sanity)")
            else:
                self.print(f"Skill '{skill_name}' not found.")
            return "refresh"
        
        if clean.startswith('inspect '):
            parts = raw.split(maxsplit=1)
            if len(parts) > 1:
                evidence_id = parts[1].strip()
                self.inspect_evidence(evidence_id)
            else:
                self.print("Usage: inspect <evidence_id>")
            return "refresh"

        # Phase 5 Commands
        if clean.startswith('analyze '):
            evidence_id = clean.replace('analyze ', '').strip()
            self.handle_analyze(evidence_id)
            return "refresh"

        if clean.startswith('autopsy '):
            target = clean.replace('autopsy ', '').strip()
            self.handle_autopsy(target)
            return "refresh"
        
        if clean in ['time', 't']:
            self.print(f"\nCurrent Time: {self.time_system.get_time_string()}")
            date_data = self.time_system.get_date_data()
            self.print(f"Date: {date_data['date_str']}")
            self.print(f"Day: {date_data['day_name']}")
            return "refresh"
        
        # Wait Command
        if clean.startswith('wait'): # Changed from input() to args
            parts = clean.split()
            mins = 15
            if len(parts) > 1 and parts[1].isdigit():
                mins = int(parts[1])
            
            self.print(f"... Waiting {mins} minutes ...")
            self.time_system.advance_time(mins)
            return "refresh"
        
        # Sleep Command
        if clean in ['s', 'sleep']:
            self.print("... Sleeping (8 hours) ...")
            # Advance 8 hours
            self.time_system.advance_time(8 * 60)
            # Recover sanity/stats here if needed
            self.player_state['sanity'] = min(self.player_state['sanity'] + 20, 100)
            self.print("You wake up feeling rested. (+20 Sanity)")
            return "refresh"
        
        # Debug Mode Commands
        if clean == 'debug':
            self.debug_mode = not self.debug_mode
            self.print(f"[DEBUG MODE: {'ON' if self.debug_mode else 'OFF'}]")
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
                    self.print("Usage: export <slot_id> <output_path>")
                return "refresh"
            
            # Debug: Set Sanity/Reality
            if clean.startswith('set'):
                parts = clean.split()
                if len(parts) >= 3:
                    stat = parts[1]
                    value = float(parts[2])
                    if stat in self.player_state:
                        self.player_state[stat] = value
                        self.print(f"[DEBUG] {stat} set to {value}")
                return "refresh"
            
            # Debug: Add XP
            if clean.startswith('addxp'):
                parts = clean.split()
                if len(parts) >= 2:
                    xp = int(parts[1])
                    self.skill_system.add_xp(xp)
                    self.print(f"[DEBUG] Added {xp} XP")
                return "refresh"
            
            # Debug: Teleport to scene
            if clean.startswith('goto'):
                parts = clean.split()
                if len(parts) >= 2:
                    scene_id = parts[1]
                    new_scene = self.scene_manager.load_scene(scene_id)
                    if new_scene:
                        self.print(f"[DEBUG] Teleported to {scene_id}")
                        self.log_event("scene_entry", scene_id=scene_id, scene_name=new_scene.get("name", "Unknown"))
                    else:
                        self.print(f"[DEBUG] Scene '{scene_id}' not found")
                return "refresh"
        
        # Theory Resolution Commands
        if clean.startswith('prove '):
            parts = raw.split(maxsplit=1)
            if len(parts) > 1:
                theory_id = parts[1].strip()
                if self.board.resolve_theory(theory_id, True):
                    self.print(f"[THEORY PROVEN: {theory_id}]")
                else:
                    self.print(f"[ERROR: Theory '{theory_id}' not found]")
            return "refresh"
        
        if clean.startswith('disprove '):
            parts = raw.split(maxsplit=1)
            if len(parts) > 1:
                theory_id = parts[1].strip()
                if self.board.resolve_theory(theory_id, False):
                    self.print(f"[THEORY DISPROVEN: {theory_id}]")
                else:
                    self.print(f"[ERROR: Theory '{theory_id}' not found]")
            return "refresh"
        
        if clean.startswith('evidence '):
            parts = raw.split()
            if len(parts) >= 3:
                theory_id = parts[1]
                evidence_id = parts[2]
                if self.board.add_evidence_to_theory(theory_id, evidence_id):
                    self.print(f"[Evidence linked to theory]")
                else:
                    self.print(f"[ERROR: Could not link evidence]")
            else:
                self.print("Usage: evidence <theory_id> <evidence_id>")
            return "refresh"
        
        if clean.startswith('talk '):
            parts = raw.split(maxsplit=1)
            if len(parts) > 1:
                dialogue_id = parts[1].strip()
                self.start_dialogue(dialogue_id)
            else:
                self.print("Usage: talk <dialogue_id>")
            return "refresh"
        
        if clean.startswith('contradict '):
            parts = raw.split()
            if len(parts) >= 3:
                theory_id = parts[1]
                evidence_id = parts[2]
                result = self.board.add_contradiction_to_theory(theory_id, evidence_id)
                if result.get('success'):
                    self.print(f"[{result['message']}]")
                    if result.get('sanity_damage', 0) > 0:
                        self.player_state['sanity'] -= result['sanity_damage']
                        self.print(f"[SANITY -{result['sanity_damage']}]")
                else:
                    self.print(f"[ERROR: {result.get('message', 'Could not add contradiction')}]")
            else:
                self.print("Usage: contradict <theory_id> <evidence_id>")
            return "refresh"
        
        # Endgame Commands
        if clean in ['submit_report', 'submit']:
            self.player_state["event_flags"].add("submit_report")
            self.print("[You prepare to submit your final report...]")
            return "refresh"
        
        if clean in ['leave_town', 'leave']:
            self.player_state["event_flags"].add("leave_town")
            self.print("[You pack your bags and prepare to leave Tyger Tyger...]")
            return "refresh"

        # Numeric Choices
        if raw.isdigit():
            idx = int(raw) - 1
            
            # Check scene choices
            if 0 <= idx < len(choices):
                return choices[idx]
            
            # Check connected paths (Local Scenes)
            connected = self.scene_manager.get_available_scenes()
            num_choices = len(choices)
            if self.input_mode == InputMode.INVESTIGATION and connected:
                path_idx = idx - num_choices
                if 0 <= path_idx < len(connected):
                    route = connected[path_idx]
                    if route["accessible"]:
                        return {"next_scene_id": route["id"]}
                    else:
                        self.print("That path is blocked.")
                        return "refresh"
            
            # Check World Travel (Locations)
            if self.input_mode == InputMode.INVESTIGATION and hasattr(self, 'location_choice_map'):
                user_choice_num = idx + 1
                if user_choice_num in self.location_choice_map:
                    loc_id = self.location_choice_map[user_choice_num]
                    self.go_to_location(loc_id)
                    return "refresh"
            
            self.print("Invalid choice number.")
            return "refresh"

        # Parser Handling
        if self.input_mode == InputMode.INVESTIGATION:
            parsed_commands = self.parser.normalize(raw)
            if parsed_commands:
                for verb, target in parsed_commands:
                    if verb:
                        self.handle_parser_command(verb, target)
                return "refresh" # Stay in same scene (or refresh state)
            else:
                self.print("I don't understand that command.")
        else:
            self.print("Use numbered choices in Dialogue Mode (or type 'switch').")
        
        return "refresh"

    def toggle_mode(self):
        if self.input_mode == InputMode.DIALOGUE:
            self.input_mode = InputMode.INVESTIGATION
            print("[Switched to INVESTIGATION mode]")
        else:
            self.input_mode = InputMode.DIALOGUE
            print("[Switched to DIALOGUE mode]")

    def toggle_thermal(self):
        self.player_state["thermal_mode"] = not self.player_state["thermal_mode"]
        state = "ON" if self.player_state["thermal_mode"] else "OFF"
        print(f"[THERMAL OPTICS: {state}]")

    def handle_parser_command(self, verb, target):
        scene = self.scene_manager.current_scene_data
        objects = scene.get("objects", {})
        
        self.print(f"\n[ACTION: {verb} {target or ''}]")

        # --- NAVIGATION ---
        if verb == "GO":
            if not target:
                self.print("Go where?")
                return
            
            # Check locations
            loc_id = self.location_manager.find_location_by_name(target)
            if loc_id:
                self.go_to_location(loc_id)
                return
            
            # Check local scene paths
            connected = self.scene_manager.get_available_scenes()
            for route in connected:
                if target.lower() in route["name"].lower():
                    if route["accessible"]:
                        self.scene_manager.load_scene(route["id"])
                        return
                    else:
                        self.print(f"The path to {route['name']} is blocked.")
                        return

            self.print(f"You can't go to '{target}' from here.")
            return

        # --- INVESTIGATION ---
        elif verb == "EXAMINE":
            if not target:
                self.display_scene()
                return
            
            obj_key, obj_data = self._resolve_object(target, objects)
            if obj_data:
                self._examine_object(obj_key, obj_data)
            else:
                 # Check inventory
                item = self.inventory_system.get_item_by_name(target)
                if item:
                    self.print(f"[INVENTORY] {item.name}: {item.description}")
                    if item.effects: self.print(f"Effects: {item.effects}")
                
                # Check evidence
                elif target.startswith("photo"): # Hacky check for evidence IDs or names?
                     self.print(f"You don't see '{target}' here.")
                else: 
                     self.print(f"You don't see '{target}' here.")

        elif verb == "SEARCH":
            self.search_location()
            # Also reveal hidden objects?
            visible = [k for k in objects.keys()]
            if visible:
                self.print(f"You notice: {', '.join(visible)}")
            else:
                self.print("Nothing of note stands out.")

        elif verb == "PHOTOGRAPH":
             has_camera = any(i.name.lower() == "camera" for i in self.inventory_system.carried_items)
             if not has_camera:
                 self.print("You need a camera to do that.")
                 return
             
             self.print(f"You snap a photo of {target or 'the scene'}.")
             # Create evidence
             timestamp = int(self.time_system.current_time.timestamp())
             ev_id = f"photo_{int(timestamp)}"
             target_desc = f"of {target}" if target else "of the scene"
             
             evidence = Evidence(
                 id=ev_id,
                 name=f"Photo {target_desc}",
                 description=f"A polarized photo {target_desc} taken at {self.scene_manager.current_scene_data.get('name', 'Unknown')}.",
                 type="visual",
                 timestamp=timestamp,
                 case_id="general"
             )
             self.inventory_system.add_evidence(evidence)

        elif verb == "COLLECT" or verb == "TAKE":
            if not target:
                self.print("Collect what?")
                return
            
            obj_key, obj_data = self._resolve_object(target, objects)
            if obj_data:
                # Create Item
                new_item = Item(
                    id=obj_key,
                    name=obj_data.get("name", obj_key),
                    type=obj_data.get("type", "tool"),
                    description=obj_data.get("description", "A collected item."),
                    effects=obj_data.get("effects", {}),
                    tags=obj_data.get("tags", [])
                )
                self.inventory_system.add_item(new_item)
                self.print(f"You pick up the {new_item.name}.")
                self.player_state["event_flags"].add(f"collected_{obj_key}") # Mark as collected
            else:
                self.print(f"You can't take '{target}'.")

        elif verb == "EQUIP":
            if not target:
                self.print("Equip what?")
                return
            if self.inventory_system.equip_item(target):
                self.print(f"You equip the {target}.")
            else:
                self.print(f"You don't have a '{target}' to equip.")

        elif verb == "UNEQUIP":
            if not target:
                self.print("Unequip what?")
                return
            if self.inventory_system.unequip_item(target):
                self.print(f"You stow the {target}.")
            else:
                self.print(f"You aren't equipping a '{target}'.")

        elif verb == "ANALYZE":
             self.handle_analyze(target)

        elif verb == "COMBINE":
             self.print("You try to combine them, but nothing happens. (Not implemented yet)")

        elif verb == "USE":
            if not target:
                self.print("Use what?")
                return
            
            # Simple use logic for now
            obj_key, obj_data = self._resolve_object(target, objects)
            if obj_data and "interactions" in obj_data and "use" in obj_data["interactions"]:
                self.print(obj_data["interactions"]["use"])
            else:
                # Try inventory item
                item = self.inventory_system.get_item_by_name(target)
                if item:
                    if item.use():
                        self.print(f"You use the {item.name}.")
                    else:
                        self.print(f"The {item.name} is out of uses.")
                else:
                    self.print(f"You can't use '{target}' here.")

        # --- SYSTEM ---
        elif verb == "MAP":
            self.display_map()
        elif verb == "WHERE":
            self.display_current_location()
        elif verb == "INVENTORY":
            self.inventory_system.list_inventory()
        elif verb == "HELP":
            self.print("\n-=- AVAILABLE COMMANDS -=-")
            self.print(" INVESTIGATION: EXAMINE [target], SEARCH, COLLECT [item], EQUIP [item], ANALYZE [evidence]")
            self.print(" ACTIONS: PHOTOGRAPH [target], USE [target] (on [target])")
            self.print(" NAVIGATION: MAP, WHERE, [number], GO [location]")
            self.print(" SYSTEM: (b)oard, (c)haracter, (i)nventory, (e)vidence, (w)ait, (s)leep, (q)uit")
            self.print("--------------------------")

        elif verb == "TALK" or verb == "ASK":
             # Need to restore TALK/ASK because it's in original
             if not target:
                self.print("Talk to whom?")
                return
             npc_key, npc_data = self._resolve_object(target, objects)
             if npc_data and npc_data.get("type") == "npc":
                 if "dialogue_id" in npc_data:
                     self.start_dialogue(npc_data["dialogue_id"])
                 else:
                     self.print(f"{npc_key} has nothing to say.")
             else:
                 self.print(f"You can't talk to '{target}'.")
        
        # --- PSYCHOLOGICAL COMMANDS (Week 15) ---
        elif verb == "MENTAL" or verb == "PSYCH":
            self.print(self.psych_state.get_psychological_summary())
        
        elif verb == "GROUND":
            self.perform_grounding_ritual()

        else:
            self.print(f"You try to {verb} the {target or 'air'}, but nothing happens yet.")
    
    def perform_grounding_ritual(self):
        """Allow player to perform a grounding ritual to reduce Mental Load."""
        import json
        
        # Load grounding rituals
        rituals_path = resource_path(os.path.join('data', 'activities', 'grounding_rituals.json'))
        if not os.path.exists(rituals_path):
            self.print("You try to ground yourself, but can't focus.")
            return
        
        with open(rituals_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            rituals = data.get("rituals", [])
        
        if not rituals:
            self.print("No grounding techniques available.")
            return
        
        # Display available rituals
        self.print("\n=== GROUNDING TECHNIQUES ===")
        for i, ritual in enumerate(rituals, 1):
            self.print(f"{i}. {ritual['name']} ({ritual['time_cost_minutes']} min, -{ritual['mental_load_reduction']} Mental Load)")
            self.print(f"   {ritual['description']}")
        
        self.print("\nChoose a technique (number) or 'cancel':")
        # Note: In the actual game loop, this would need to be handled via the input system
        # For now, we'll just show the first ritual as an example
        
        # Auto-select first ritual for demonstration
        ritual = rituals[0]
        self.print(f"\n[Performing: {ritual['name']}]")
        
        # Check requirements
        requirements = ritual.get("requirements", {})
        can_perform = True
        
        if requirements.get("has_evidence") and not self.inventory_system.carried_items:
            can_perform = False
            self.print("You don't have any evidence to review.")
        
        if requirements.get("has_notebook"):
            # Assume player has notebook for now
            pass
        
        if not can_perform:
            self.print(ritual.get("failure_text", "You can't perform this technique right now."))
            return
        
        # Perform the ritual
        self.time_system.advance_time(ritual["time_cost_minutes"])
        
        # Reduce Mental Load
        reduction = ritual["mental_load_reduction"]
        result = self.psych_state.reduce_mental_load(reduction, ritual["name"])
        
        self.print(f"\n{ritual.get('success_text', 'You feel slightly better.')}")
        for msg in result.get("messages", []):
            self.print(msg)

    def _resolve_object(self, target_name: str, objects: dict):
        """Helper to fuzzy match an object name in the current scene."""
        if not target_name: return None, None
        
        # Exact match
        if target_name in objects:
            return target_name, objects[target_name]
            
        # Partial match
        for k, v in objects.items():
            if target_name.lower() in k.lower():
                return k, v
                
        return None, None
    
    def _examine_object(self, target_key: str, obj_data: dict):
        desc = obj_data.get("description", "You see nothing special.")
        
        # Thermal Mode Override
        if self.player_state.get("thermal_mode", False):
            # Get temperature from object data or default to ambient
            temp = obj_data.get("temperature", 70.0)
            self.print(f"[THERMAL READING: {temp:.1f}°F]")
            
            if temp > 99.1:
                self.print(">> ANOMALOUS HEAT DETECTED <<")
                # Passive Medicine Check
                check = self.skill_system.roll_check("Medicine", 10, manual_roll=None)
                if check["success"]:
                    self.print("[MEDICINE] This heat isn't natural. It's radiating from the inside out.")
            
        self.print(f"{desc}")
        
        # Passive Checks
        if "passive_checks" in obj_data:
            for check in obj_data["passive_checks"]:
                # Silent check: 2d6 + Skill >= DC
                skill_name = check["skill"]
                dc = check["difficulty"]
                
                # We use 'roll_check' but treat it silently unless success
                result = self.skill_system.roll_check(skill_name, dc, manual_roll=None)
                if result["success"]:
                    self.print(f"\n[{skill_name.upper()} SUCCESS] {check['success_text']}")

        # Interactions
        if "interactions" in obj_data:
            self.print(f"You could also: {', '.join(obj_data['interactions'].keys()).upper()}")

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

    def display_dialogue(self):
        data = self.dialogue_manager.get_render_data()
        if not data:
            self.in_dialogue = False
            return

        self.print("\n" + "-"*40)
        self.print(f"[{data['speaker']}]: \"{data['text']}\"")
        
        for interjection in data['interjections']:
            self.print(f" > {interjection}")
            
        self.print("-" * 40)
        
        choices = data['choices']
        for idx, c in enumerate(choices):
            status = "" if c['enabled'] else f"(BLOCKED {c['reason']})"
            self.print(f"{idx+1}. {c['text']} {status}")
            
        self.print("\n(Enter Number, 'ask about <topic>', 'say <text>', or /debug)")

    def process_dialogue_input(self, raw_input):
        """Process dialogue input - supports both numbered choices and parser commands."""
        success, msg = self.dialogue_manager.process_input(raw_input)
        
        if success:
            if msg == "DEBUG_TOGGLE":
                return  # Just refresh
            elif msg == "EXIT":
                self.in_dialogue = False
                self.print("... Dialogue Ended ...")
            elif msg == "NEXT":
                # Continue to next node, display will refresh
                pass
            elif msg.startswith("SCENE:"):
                # Scene transition
                scene_id = msg.split(":")[1]
                self.in_dialogue = False
                self.scene_manager.load_scene(scene_id)
            elif msg.startswith("CLUE_REVEALED:"):
                # NPC revealed knowledge
                clue_id = msg.split(":")[1]
                self.print(f"\n[CLUE DISCOVERED: {clue_id}]")
                # TODO: Add clue to journal/inventory
        else:
            self.print(f"{msg}")

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

    def handle_analyze(self, evidence_id: str):
        """Perform formal analysis on evidence to check for reliability and details."""
        evidence = self.inventory_system.evidence_collection.get(evidence_id)
        if not evidence:
            self.print(f"Evidence '{evidence_id}' not found.")
            return

        # 1. Reliability Check (Skepticism)
        if not evidence.is_reliable and not evidence.reliability_detected:
            # Secret check to see if player notices it's planted/fake
            result = self.skill_system.roll_check("Skepticism", 9)
            if result["success"]:
                evidence.reliability_detected = True
                self.print(f"\n[CRYSTAL CLARITY] Your Skepticism notices something off about {evidence.name}...")
                self.print(" This evidence appears to have been PLANTED or FAKED.")
            else:
                self.print(f"\nYou analyze {evidence.name} but find nothing suspicious about its origin.")
        
        # 2. Skill Analysis (if applicable)
        for skill in evidence.related_skills:
            if skill not in evidence.analysis_results:
                # Automate check for simplicity or ask for a specific command?
                # Let's do a quick automated check if they have the skill at a decent level.
                res = self.skill_system.roll_check(skill, 10)
                if res["success"]:
                    detail = f"Detailed analysis confirms relevant find for {skill}." # Placeholder
                    evidence.analyze_with_skill(skill, detail)
                    self.print(f"[SUCCESS] {skill} analysis: {detail}")
                else:
                    self.print(f"[FAILURE] {skill} analysis was inconclusive.")

    def handle_autopsy(self, target: str):
        """Manages the autopsy minigame interaction."""
        # Simple implementation: expect 'autopsy body_id [zone_index]'
        parts = target.split()
        if not parts:
            self.print("Usage: autopsy <body_id> [zone_index]")
            return
        
        body_id = parts[0]
        # Check if we have the body (as evidence or special item)
        # For now, let's assume it's in inventory_system.carried_items or evidence_collection
        # Or just a hardcoded check for the test scene body.
        
        if not self.current_autopsy or self.current_autopsy.body_id != body_id:
            # Start new minigame
            self.current_autopsy = AutopsyMinigame(body_id, "Subject 347", self.skill_system, self.inventory_system)
            self.print(f"\n--- Starting Autopsy: {self.current_autopsy.body_name} ---")
        
        if len(parts) == 1:
            # Show status
            self.current_autopsy.run_minigame(self.print)
            return

        # Try to examine a zone
        try:
            zone_idx = int(parts[1]) - 1
            zones = list(self.current_autopsy.ZONES.keys())
            if 0 <= zone_idx < len(zones):
                zone_name = zones[zone_idx]
                res = self.current_autopsy.examine_zone(zone_name)
                self.print(f"\n{res['message']}")
                if res['success']:
                    self.print(f"Findings: {res['findings']}")
                    # Add findings as evidence
                    new_ev = Evidence(res['evidence_id'], res['findings'], "medical", name=f"Autopsy: {zone_name}")
                    self.inventory_system.add_evidence(new_ev)
                
                self.print(f"Body Integrity: {self.current_autopsy.integrity}%")
            elif zone_idx == len(zones):
                msg = self.current_autopsy.conclude()
                self.print(f"\n{msg}")
                self.current_autopsy = None
            else:
                self.print("Invalid zone index.")
        except ValueError:
            self.print("Zone must be a number.")

    def show_board(self):
        """Display The Board with visual ASCII art."""
        print(self.board_ui.render())
        print("\nCommands: 'evidence <theory_id> <evidence_id>' | 'contradict <theory_id> <evidence_id>'")
        print("          'prove <theory_id>' | 'disprove <theory_id>'\n")

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

    # Week 14: Theory Discovery
    def check_theory_unlocks(self):
        """Check if new theories can be discovered based on current game state."""
        game_state = self.get_game_state()
        # Add inventory and visited scenes to game_state
        game_state["inventory_system"] = self.inventory_system
        game_state["visited_scenes"] = self.scene_manager.visited_scenes if hasattr(self.scene_manager, 'visited_scenes') else set()
        
        newly_discovered = []
        
        for theory_id, theory in self.board.theories.items():
            if theory.status == "locked":
                if self.board.can_discover_theory(theory_id, game_state):
                    theory.status = "available"
                    newly_discovered.append(theory)
        
        # Notify player of discoveries
        for theory in newly_discovered:
            self.print(f"\\n[THEORY DISCOVERED] {theory.name}")
            self.print(f"   {theory.description}")
    
    # Week 14: Theory Management Commands
    def display_theories(self):
        """Display available and active theories."""
        self.print("\\n=== THEORIES ===\\n")
        
        # Active/Internalizing
        active = [t for t in self.board.theories.values() if t.status in ["active", "internalizing"]]
        if active:
            self.print("ACTIVE/INTERNALIZING:")
            for theory in active:
                status_str = theory.status.upper()
                if theory.status == "internalizing":
                    progress = theory.internalization_progress_minutes
                    required = theory.internalize_time_hours * 60
                    pct = int((progress / required) * 100)
                    status_str += f" ({pct}% - {required - progress}min remaining)"
                
                self.print(f"  [{theory.id}] {theory.name} - {status_str}")
                self.print(f"      {theory.description}")
                
                if not theory.hidden_effects:
                    effects_str = ", ".join([f"{k} {'+' if v > 0 else ''}{v}" for k, v in theory.effects.items()])
                    self.print(f"      Effects: {effects_str}")
                self.print()
        
        # Available
        available = [t for t in self.board.theories.values() if t.status == "available"]
        if available:
            self.print("AVAILABLE:")
            for theory in available:
                self.print(f"  [{theory.id}] {theory.name}")
                self.print(f"      {theory.description}")
                self.print(f"      Internalization Time: {theory.internalize_time_hours}h")
                self.print()
    
    def internalize_theory(self, theory_id: str):
        """Start internalizing a theory."""
        success = self.board.start_internalizing(theory_id)
        if success:
            theory = self.board.get_theory(theory_id)
            self.print(f"\\n🧠 You've begun to internalize '{theory.name}'.")
            self.print(f"   This will take {theory.internalize_time_hours} hours of contemplation.")
            
            # Apply immediate effects if any
            messages = self.board.apply_internalize_effects(theory_id, self)
            for msg in messages:
                self.print(f"   {msg}")
    
    def abandon_theory(self, theory_id: str):
        """Abandon an active theory."""
        theory = self.board.get_theory(theory_id)
        if not theory:
            self.print("Theory not found.")
            return
        
        if theory.status not in ["active", "internalizing"]:
            self.print(f"'{theory.name}' is not currently active.")
            return
        
        # Mental cost for abandoning
        self.player_state["sanity"] -= 5
        self.print(f"\\n💭 You abandon '{theory.name}'. The mental whiplash stings.")
        self.print("   [SANITY -5]")
        
        theory.status = "available"
        theory.internalization_progress_minutes = 0
