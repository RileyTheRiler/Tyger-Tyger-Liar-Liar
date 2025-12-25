#!/usr/bin/env python3
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "engine"))

from engine.scene_manager import SceneManager
from engine.text_composer import TextComposer, Archetype

def main():
    if len(sys.argv) < 2:
        print("Usage: python scene_debugger.py <scene_file.json>")
        sys.exit(1)

    scene_path = sys.argv[1]

    # Mock Systems
    class MockSystem:
        def __init__(self):
            self.skills = {
                "Paranormal Sensitivity": 10,
                "Logic": 5,
                "Skepticism": 5
            }
            self.in_flashback = False
        def get_skill(self, name):
            class Skill:
                def __init__(self, val): self.effective_level = val
            return Skill(self.skills.get(name, 0))
        def roll_check(self, skill, dc): return {"success": True}
        def enter_flashback(self, pov): pass
        def exit_flashback(self): pass

    class MockBoard:
        def __init__(self): self.theories = {}
        def get_theory(self, tid): return None

    class MockTime:
        def __init__(self):
            from datetime import datetime
            self.current_time = datetime(1999, 10, 15, 12, 0)
            self.weather = "clear"

    player_state = {
        "sanity": 100.0,
        "reality": 100.0,
        "event_flags": set(),
        "skills": {"Paranormal Sensitivity": 10, "Logic": 5}
    }

    manager = SceneManager(MockTime(), MockBoard(), MockSystem(), player_state, MockSystem())
    composer = TextComposer(MockSystem(), MockBoard(), player_state)

    # Load Scene
    try:
        with open(scene_path, 'r') as f:
            data = json.load(f)
            # Wrap in list if single object, or handle appropriately
            if isinstance(data, dict):
                scenes = [data]
            else:
                scenes = data

            for s in scenes:
                manager.scenes[s['id']] = s

            # Load first scene
            scene_id = scenes[0]['id']
            loaded = manager.load_scene(scene_id)

            print(f"\nLoaded Scene: {scene_id}")
            print("-" * 40)

            # Compose Text
            result = composer.compose(loaded["text"], Archetype.NEUTRAL, player_state)
            print("COMPOSED TEXT:\n")
            print(result.full_text)
            print("-" * 40)

            # Check Parser Triggers
            print("TESTING PARSER INPUT:")
            while True:
                user_input = input("Enter command (or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    break

                parts = user_input.split(maxsplit=1)
                verb = parts[0]
                target = parts[1] if len(parts) > 1 else ""

                trigger = manager.check_parser_triggers(verb, target)
                if trigger:
                    print(f"MATCH! Response: {trigger.get('response')}")
                else:
                    print("No trigger match.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
