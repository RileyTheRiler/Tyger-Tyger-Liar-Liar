#!/usr/bin/env python3
"""
Scene Writing Tooling
---------------------
CLI for authoring, validating, and previewing scenes.

Usage:
  python tools/scene_tool.py build <output_file>
  python tools/scene_tool.py preview <scene_file> [--id <scene_id>] [--lens <type>] [--skills <skill:lvl,...>]
  python tools/scene_tool.py compare <scene_file> [--id <scene_id>]
  python tools/scene_tool.py validate <scene_file>
  python tools/scene_tool.py template <type> <output_file>
"""

import argparse
import json
import sys
import os
from enum import Enum

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "../src")
sys.path.append(src_path)

try:
    from engine.text_composer import TextComposer, Archetype, ComposedText
    from content.schema_validator import SchemaValidator
    from ui.interface import Colors, print_separator, print_boxed_title
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Ensure you are running this from the repo root or tools/ directory.")
    sys.exit(1)

# Templates (same as before)
TEMPLATES = {
    "witness": {
        "id": "scene_witness_template",
        "title": "Witness Interview: [Name]",
        "location_id": "loc_police_station",
        "text": {
            "base": "You sit across from [Name]. They look nervous.",
            "lens": {
                "believer": "Their aura is fractured. They've seen something they can't process.",
                "skeptic": "Classic signs of stress. Dilated pupils, tapping foot. They're hiding something mundane.",
                "haunted": "You know that look. It's the same one you see in the mirror."
            },
            "inserts": [
                {
                    "text": "They keep glancing at the door.",
                    "condition": {"skill_gte": {"Psychology": 4}},
                    "insert_at": "AFTER_BASE"
                }
            ]
        },
        "choices": [
            {
                "label": "Ask about the incident",
                "next_scene": "scene_witness_incident"
            },
            {
                "label": "[Intimidation] Press them for details",
                "check": {
                    "skill": "Intimidation",
                    "dc": 8,
                    "success_scene": "scene_witness_confess",
                    "failure_scene": "scene_witness_silent"
                }
            }
        ]
    },
    "crime_scene": {
        "id": "scene_crime_template",
        "title": "Crime Scene: [Location]",
        "location_id": "loc_crime_scene",
        "text": {
            "base": "The area is taped off. Evidence markers are placed on the ground.",
            "lens": {
                "believer": "The air is heavy. A residue of violence hangs like static.",
                "skeptic": "Standard procedure. Forensics team is already sweeping.",
                "haunted": "The blood pattern looks familiar. Too familiar."
            },
            "passive_clues": [
                {
                    "clue_id": "clue_strange_symbol",
                    "visible_when": {"skill_gte": {"Occult": 3}}
                }
            ]
        },
        "choices": [
            {"label": "Examine the body", "next_scene": "scene_examine_body"},
            {"label": "Search the perimeter", "next_scene": "scene_search_perimeter"}
        ]
    },
    "dream": {
        "id": "scene_dream_template",
        "title": "Dream Sequence",
        "text": {
            "base": "You are falling. The sky is the color of a bruised plum.",
            "lens": {
                "believer": "This isn't a dream. It's a visitation.",
                "skeptic": "REM sleep. Stress processing. Nothing more.",
                "haunted": "The fall never ends. It never has."
            }
        },
        "choices": [
            {"label": "Wake up", "next_scene": "scene_hotel_room_morning"}
        ]
    },
    "entity": {
        "id": "scene_entity_template",
        "title": "Encounter: [Entity Name]",
        "text": {
            "base": "Something steps out of the shadows. It shouldn't exist.",
            "lens": {
                "believer": "A manifestation of the Other. Pure entropy.",
                "skeptic": "A trick of the light. A hallucination caused by fatigue.",
                "haunted": "It has your father's eyes."
            },
            "inserts": [
                {
                    "text": "Your geiger counter clicks frantically.",
                    "condition": {"equipment": "item_geiger_counter"},
                    "insert_at": "AFTER_BASE"
                }
            ]
        },
        "encounter_id": "encounter_shadow_beast",
        "choices": [
            {"label": "Run", "next_scene": "scene_chase_start"},
            {"label": "Fight", "next_scene": "scene_combat_start"}
        ]
    }
}

def parse_skills(skill_str):
    if not skill_str:
        return {}
    skills = {}
    for pair in skill_str.split(','):
        if ':' in pair:
            name, lvl = pair.split(':')
            skills[name.strip()] = int(lvl)
    return skills

def load_scenes(filepath):
    """
    Loads scenes from a file. Handles both single dict and list of dicts.
    Returns a list of scene dictionaries.
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return []

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Determine if it's a scene or a container
        if "id" in data and "text" in data:
            return [data]
        else:
            # Maybe check if it has keys that are scenes?
            # For now assume if it's not a scene structure, it might be invalid or empty
            return []
    return []

def check_style(scene_data):
    warnings = []
    text_data = scene_data.get("text", {})
    lens_data = text_data.get("lens", {})
    inserts = text_data.get("inserts", [])
    choices = scene_data.get("choices", [])

    scene_id = scene_data.get("id", "unknown")

    # Word count
    base_text = text_data.get("base", "")
    word_count = len(base_text.split())
    if lens_data:
        for text in lens_data.values():
            word_count += len(text.split())

    # Check for missing lens variants
    for lens in ["believer", "skeptic", "haunted"]:
        if not lens_data or lens not in lens_data or not lens_data[lens]:
            warnings.append(f"[{scene_id}] Missing lens variant: '{lens}'.")

    # Check for sensory details
    base_text_lower = base_text.lower()
    sensory_keywords = ["smell", "sound", "hear", "see", "taste", "feel", "cold", "hot", "dark", "light", "metallic", "blood", "shadow"]
    if not any(w in base_text_lower for w in sensory_keywords):
        warnings.append(f"[{scene_id}] Base text lacks sensory keywords.")

    # Check for impossible or contradictory conditions
    for i, insert in enumerate(inserts):
        condition = insert.get("condition", {})
        if "skill_gte" in condition:
            for skill, lvl in condition["skill_gte"].items():
                if lvl > 10:
                    warnings.append(f"[{scene_id}] Insert #{i+1} requires {skill} > {lvl}, which may be unreachable.")

        # Check for empty condition (always true) if explicitly empty dict, though None means always true too usually.
        # Just a note.

    # Check choices for high DC
    for i, choice in enumerate(choices):
        check = choice.get("check")
        if check:
            dc = check.get("dc", 0)
            if dc > 15: # 15 is very high difficulty
                 warnings.append(f"[{scene_id}] Choice #{i+1} has very high DC ({dc}).")
            if dc > 20:
                 warnings.append(f"[{scene_id}] Choice #{i+1} has DC {dc}, likely impossible.")

    return warnings, word_count

def preview_scene(filepath, target_id=None, lens_str="neutral", skills=None):
    scenes = load_scenes(filepath)
    if not scenes:
        return

    target_scene = None
    if target_id:
        target_scene = next((s for s in scenes if s.get("id") == target_id), None)
        if not target_scene:
            print(f"Scene ID '{target_id}' not found in {filepath}")
            return
    else:
        if len(scenes) > 1:
            print(f"File contains {len(scenes)} scenes. Showing first scene '{scenes[0].get('id')}'. Use --id to specify.")
        target_scene = scenes[0]

    scene_data = target_scene

    # Mock player state
    player_state = {
        "skills": skills or {"Logic": 3, "Perception": 3, "Psychology": 3, "Forensics": 3, "Occult": 1},
        "flags": {},
        "inventory": ["item_flashlight"],
        "active_theories": []
    }

    # Determine lens
    archetype_map = {
        "believer": Archetype.BELIEVER,
        "skeptic": Archetype.SKEPTIC,
        "haunted": Archetype.HAUNTED,
        "neutral": Archetype.NEUTRAL
    }
    archetype = archetype_map.get(lens_str.lower(), Archetype.NEUTRAL)

    composer = TextComposer()
    result = composer.compose(scene_data, archetype, player_state)

    print_separator(color=Colors.CYAN)
    print_boxed_title(scene_data.get("title", "Untitled Scene"), color=Colors.CYAN)
    print(f"ID: {scene_data.get('id')}")

    # Print content with colors
    print(f"\n{Colors.WHITE}{result.full_text}{Colors.RESET}\n")

    # Print choices
    if "choices" in scene_data:
        print(f"{Colors.YELLOW}Choices:{Colors.RESET}")
        for i, choice in enumerate(scene_data["choices"]):
            label = choice.get("label", "Continue")
            check = choice.get("check")
            if check:
                print(f" {i+1}. [{check.get('skill')} DC {check.get('dc')}] {label}")
            else:
                print(f" {i+1}. {label}")

    print_separator(color=Colors.CYAN)

    # Debug info
    print(f"{Colors.MAGENTA}Debug Info:{Colors.RESET}")
    print(f" Lens: {result.lens_used}")
    print(f" Inserts: {result.inserts_applied}")
    print(f" Fracture: {result.fracture_applied}")

def compare_scene(filepath, target_id=None):
    """
    Renders the scene for all archetypes side-by-side (or sequentially).
    """
    scenes = load_scenes(filepath)
    if not scenes:
        return

    scenes_to_process = []
    if target_id:
        target_scene = next((s for s in scenes if s.get("id") == target_id), None)
        if not target_scene:
            print(f"Scene ID '{target_id}' not found.")
            return
        scenes_to_process = [target_scene]
    else:
        scenes_to_process = scenes

    composer = TextComposer()
    # Mock state
    player_state = {
        "skills": {"Logic": 3, "Perception": 3, "Psychology": 3, "Forensics": 3, "Occult": 1},
        "flags": {},
        "inventory": [],
        "active_theories": []
    }
    archetypes = [Archetype.NEUTRAL, Archetype.BELIEVER, Archetype.SKEPTIC, Archetype.HAUNTED]

    for scene_data in scenes_to_process:
        print("\n" + "="*60)
        print(f"SCENE: {scene_data.get('title', 'Untitled')} (ID: {scene_data.get('id')})")
        print("="*60)

        # Calculate Base Word Count (without inserts)
        base_text = scene_data.get("text", {}).get("base", "")
        print(f"Base Text Length: {len(base_text.split())} words")

        for arc in archetypes:
            result = composer.compose(scene_data, arc, player_state)
            text = result.full_text
            word_count = len(text.split())

            color = Colors.WHITE
            if arc == Archetype.BELIEVER: color = Colors.CYAN
            elif arc == Archetype.SKEPTIC: color = Colors.YELLOW
            elif arc == Archetype.HAUNTED: color = Colors.RED

            print(f"\n{color}--- {arc.name} ({word_count} words) ---{Colors.RESET}")
            print(f"{text}")

def validate_file(filepath):
    validator = SchemaValidator()
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Validate schema
        # The validator handles lists if we pass individual scenes?
        # SchemaValidator.validate_scene expects a single scene.

        scenes = []
        if isinstance(data, list):
            scenes = data
        else:
            scenes = [data]

        all_valid = True

        for i, scene in enumerate(scenes):
            valid, errors = validator.validate_scene(scene)
            sid = scene.get('id', f'Index {i}')

            if not valid:
                all_valid = False
                print(f"{Colors.RED}[FAIL] Schema Validation for {sid}:{Colors.RESET}")
                for err in errors:
                    print(f" - {err}")
            else:
                # print(f"{Colors.GREEN}[PASS] Schema Validation for {sid}{Colors.RESET}")
                pass

            # Style check
            warnings, word_count = check_style(scene)
            if warnings:
                 print(f"{Colors.YELLOW}[WARN] Style for {sid} ({word_count} words):{Colors.RESET}")
                 for w in warnings:
                     print(f" - {w}")
            else:
                 print(f"{Colors.GREEN}[PASS] {sid} ({word_count} words){Colors.RESET}")

        if all_valid:
            print(f"\n{Colors.GREEN}All scenes passed schema validation.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Some scenes failed validation.{Colors.RESET}")

    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Invalid JSON: {e}{Colors.RESET}")

def create_template(template_type, output_path):
    if template_type not in TEMPLATES:
        print(f"Unknown template type: {template_type}")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        return

    data = TEMPLATES[template_type]

    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        return

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Created {template_type} template at {output_path}")

def build_interactive(output_path):
    print("Interactive Scene Builder")
    scene_id = input("Scene ID: ")
    title = input("Title: ")
    base_text = input("Base Text: ")

    scene_data = {
        "id": scene_id,
        "title": title,
        "text": {
            "base": base_text,
            "lens": {},
            "inserts": []
        },
        "choices": []
    }

    print("\n--- Archetype Variants (Leave empty to skip) ---")
    for lens in ["believer", "skeptic", "haunted"]:
        text = input(f"{lens.capitalize()}: ")
        if text:
            scene_data["text"]["lens"][lens] = text

    print("\n--- Inserts ---")
    while True:
        print("Add an Insert? (y/n)")
        if not input().lower().startswith('y'):
            break

        insert_text = input("Insert Text: ")
        skill_req = input("Required Skill (e.g. Logic) [Enter to skip]: ")
        level = 0
        if skill_req:
             level = input("Skill Level (e.g. 4): ")

        position = input("Position (AFTER_BASE, AFTER_LENS, BEFORE_CHOICES) [Default: AFTER_LENS]: ")

        insert = {
            "text": insert_text,
            "insert_at": position or "AFTER_LENS"
        }

        if skill_req and level:
            insert["condition"] = {"skill_gte": {skill_req: int(level)}}

        scene_data["text"]["inserts"].append(insert)

    print("\n--- Choices ---")
    while True:
        print("Add a Choice? (y/n)")
        if not input().lower().startswith('y'):
            break

        label = input("Label: ")
        next_scene = input("Next Scene ID: ")

        choice = {"label": label, "next_scene": next_scene}

        skill_check = input("Is this a skill check? (y/n): ")
        if skill_check.lower().startswith('y'):
            skill = input("Skill: ")
            dc = input("DC: ")
            fail_scene = input("Failure Scene ID: ")
            choice["check"] = {
                "skill": skill,
                "dc": int(dc),
                "success_scene": next_scene,
                "failure_scene": fail_scene
            }
            if "next_scene" in choice:
                del choice["next_scene"]

        scene_data["choices"].append(choice)

    # Save
    with open(output_path, 'w') as f:
        json.dump(scene_data, f, indent=2)
    print(f"Saved scene to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Scene Writing Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Preview
    p_preview = subparsers.add_parser("preview", help="Preview a scene")
    p_preview.add_argument("file", help="Path to scene JSON file")
    p_preview.add_argument("--id", help="Scene ID (if file contains multiple)")
    p_preview.add_argument("--lens", default="neutral", choices=["neutral", "believer", "skeptic", "haunted"])
    p_preview.add_argument("--skills", help="Comma-separated skills (e.g. Logic:5,Perception:2)")

    # Compare
    p_compare = subparsers.add_parser("compare", help="Compare scene variants side-by-side")
    p_compare.add_argument("file", help="Path to scene JSON file")
    p_compare.add_argument("--id", help="Scene ID (if file contains multiple)")

    # Validate
    p_validate = subparsers.add_parser("validate", help="Validate a scene file")
    p_validate.add_argument("file", help="Path to scene JSON file")

    # Template
    p_template = subparsers.add_parser("template", help="Generate a template")
    p_template.add_argument("type", choices=TEMPLATES.keys())
    p_template.add_argument("output", help="Output file path")

    # Build
    p_build = subparsers.add_parser("build", help="Interactive builder")
    p_build.add_argument("output", help="Output file path")

    args = parser.parse_args()

    if args.command == "preview":
        skills = parse_skills(args.skills)
        preview_scene(args.file, args.id, args.lens, skills)
    elif args.command == "compare":
        compare_scene(args.file, args.id)
    elif args.command == "validate":
        validate_file(args.file)
    elif args.command == "template":
        create_template(args.type, args.output)
    elif args.command == "build":
        build_interactive(args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
