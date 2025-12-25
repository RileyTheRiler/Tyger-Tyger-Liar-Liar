import argparse
import sys
import json
import os
import time

"""
Tyger Tyger QA Runner
=====================

A standalone tool for automated and interactive testing of the game engine.

Usage Examples:
---------------
1. Run with specific archetype and godmode (all checks pass):
   python qa_runner.py --archetype intuition --godmode

2. Test low sanity behavior:
   python qa_runner.py --set-sanity 5 --start-scene bedroom

3. Trigger specific events (e.g., fractures):
   python qa_runner.py --trigger-event fracture_flashback

4. Log all skill checks and parser intents for analysis:
   python qa_runner.py --log-checks --log-parser

Logs are saved to `logs/qa/`.
"""

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

sys.path.append(resource_path('src'))
sys.path.append(resource_path('src/engine'))
sys.path.append(resource_path('src/ui'))
sys.path.append(resource_path('src/content'))

from game import Game
from mechanics import SkillSystem, Attribute, Skill
from engine.text_composer import Archetype
from engine.input_system import CommandParser

class QAHelper:
    def __init__(self, game_instance):
        self.game = game_instance
        self.log_dir = os.path.join("logs", "qa")
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_path(self, log_name):
        return os.path.join(self.log_dir, log_name)

    def setup_archetype(self, archetype_name):
        """Sets up the character skills and stats for a specific archetype."""
        # Reset stats first
        for attr in self.game.skill_system.attributes.values():
            attr.value = 1
        for skill in self.game.skill_system.skills.values():
            skill.base_level = 0

        if archetype_name == "reason":
            self.game.player_state["archetype"] = Archetype.SKEPTIC
            self.game.skill_system.attributes["REASON"].value = 5
            self.game.skill_system.attributes["INTUITION"].value = 2
            # Set key skills
            self.game.skill_system.get_skill("Logic").base_level = 4
            self.game.skill_system.get_skill("Skepticism").base_level = 4
            self.game.skill_system.get_skill("Forensics").base_level = 3
            self.game.skill_system.get_skill("Research").base_level = 3

        elif archetype_name == "intuition":
            self.game.player_state["archetype"] = Archetype.BELIEVER
            self.game.skill_system.attributes["INTUITION"].value = 5
            self.game.skill_system.attributes["REASON"].value = 2
            # Set key skills
            self.game.skill_system.get_skill("Paranormal Sensitivity").base_level = 4
            self.game.skill_system.get_skill("Instinct").base_level = 4
            self.game.skill_system.get_skill("Empathy").base_level = 3
            self.game.skill_system.get_skill("Pattern Recognition").base_level = 3

        elif archetype_name == "trauma":
            self.game.player_state["archetype"] = Archetype.HAUNTED
            self.game.skill_system.attributes["CONSTITUTION"].value = 2
            self.game.skill_system.attributes["PRESENCE"].value = 2
            # Low Sanity Start
            self.game.player_state["sanity"] = 40.0
            # Set key skills (mixed bag, mostly defensive/survival)
            self.game.skill_system.get_skill("Endurance").base_level = 4
            self.game.skill_system.get_skill("Survival").base_level = 3
            self.game.skill_system.get_skill("Subconscious").base_level = 4

        print(f"[QA] Archetype '{archetype_name}' configured.")

    def enable_godmode(self):
        """Overrides skill system to always succeed."""
        original_roll = self.game.skill_system.roll_check

        def god_roll(skill_name, difficulty, check_type="white", check_id=None, manual_roll=None):
            # Always return a massive success
            print(f"[GODMODE] Auto-succeeding {skill_name} check.")
            return {
                "skill": skill_name,
                "roll": 12,
                "modifier": 100,
                "total": 112,
                "difficulty": difficulty,
                "success": True,
                "type": check_type,
                "blocked": False,
                "skill_level_at_attempt": 100,
                "dice": {"d1": 6, "d2": 6, "total": 12},
                "description": "GODMODE"
            }

        self.game.skill_system.roll_check = god_roll
        self.game.debug_mode = True
        print("[QA] GODMODE enabled: All skill checks will pass.")

    def trigger_event(self, event_id):
        """Manually triggers an event via TriggerManager or event flags."""
        print(f"[QA] Triggering event '{event_id}'...")

        # 1. Try to set it as a flag
        self.game.player_state["event_flags"].add(event_id)

        # 2. Check if it's a defined trigger and fire its effects
        # Special hardcoded ones for testing
        if event_id == 'aurora_surge':
            self.game.time_system.advance_time(60)
            self.game.scene_manager.apply_ambient_effects(60) # Simulate effects
            print("[QA] Aurora Surge simulated (Time advanced, ambient effects applied).")

    def run_check_logger(self):
        """Monkey patches roll_check to log results to a file."""
        original_roll = self.game.skill_system.roll_check

        def logged_roll(skill_name, difficulty, check_type="white", check_id=None, manual_roll=None):
            result = original_roll(skill_name, difficulty, check_type, check_id, manual_roll)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "skill": skill_name,
                "dc": difficulty,
                "roll": result["roll"],
                "total": result["total"],
                "outcome": "SUCCESS" if result["success"] else "FAILURE",
                "scene": self.game.scene_manager.current_scene_id,
                "sanity": self.game.player_state["sanity"]
            }

            with open(self._get_log_path("qa_check_log.json"), "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            return result

        self.game.skill_system.roll_check = logged_roll
        print(f"[QA] Check Logger enabled. Writing to '{self._get_log_path('qa_check_log.json')}'.")

    def run_parser_logger(self):
        """Monkey patches parser.normalize to log input -> intent."""
        original_normalize = self.game.parser.normalize

        def logged_normalize(input_str):
            result = original_normalize(input_str)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "input": input_str,
                "parsed_intent": result,
                "scene": self.game.scene_manager.current_scene_id
            }

            with open(self._get_log_path("qa_parser_log.json"), "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            return result

        self.game.parser.normalize = logged_normalize
        print(f"[QA] Parser Logger enabled. Writing to '{self._get_log_path('qa_parser_log.json')}'.")

    def log_board_state(self):
         board_dump = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scene": self.game.scene_manager.current_scene_id,
            "theories": [t.id for t in self.game.board.theories.values() if t.status == "active"],
            "sanity": self.game.player_state["sanity"]
        }
         with open(self._get_log_path("qa_board_log.json"), "a") as f:
            f.write(json.dumps(board_dump) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Tyger Tyger QA Runner")
    parser.add_argument('--start-scene', type=str, default="bedroom", help="Initial scene ID")
    parser.add_argument('--archetype', type=str, choices=['reason', 'intuition', 'trauma'], help="Preset character build")
    parser.add_argument('--godmode', action='store_true', help="Enable god mode (auto-pass checks)")
    parser.add_argument('--set-sanity', type=float, help="Set initial sanity level (0-100)")
    parser.add_argument('--trigger-event', type=str, help="Trigger a specific event ID at start")
    parser.add_argument('--log-checks', action='store_true', help="Log all skill checks to a file")
    parser.add_argument('--log-parser', action='store_true', help="Log parser input->intent map to a file")

    args = parser.parse_args()

    # Initialize Game
    game = Game()
    qa = QAHelper(game)

    # Apply QA Settings
    if args.archetype:
        qa.setup_archetype(args.archetype)

    if args.set_sanity is not None:
        game.player_state["sanity"] = args.set_sanity
        print(f"[QA] Sanity set to {args.set_sanity}")

    if args.godmode:
        qa.enable_godmode()

    if args.log_checks:
        qa.run_check_logger()

    if args.log_parser:
        qa.run_parser_logger()

    if args.trigger_event:
        qa.trigger_event(args.trigger_event)

    # Run Game
    print(f"[QA] Starting game in scene: {args.start_scene}")
    game.start_game(args.start_scene)

    # Simple CLI loop wrapper
    print("\n[QA] Interactive Mode. Type 'quit' to exit.")
    while True:
        try:
            user_input = input("> ")
            game.step(user_input)

            # Log board state if logging is on
            if args.log_checks: # Reuse this flag for general logging for now
                qa.log_board_state()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

        except (KeyboardInterrupt, EOFError):
            print("\n[QA] Exiting.")
            break
        except Exception as e:
            print(f"[QA CRASH] {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    main()
