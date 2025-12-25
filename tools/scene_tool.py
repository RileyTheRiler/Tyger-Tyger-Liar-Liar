#!/usr/bin/env python3
"""
Scene Writing Tooling
---------------------
CLI for authoring, validating, and previewing scenes.

Usage:
  python tools/scene_tool.py build <output_file>
  python tools/scene_tool.py preview <scene_file> [--lens <type>] [--skills <skill:lvl,...>]
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

# Templates
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

def check_style(scene_data):
    warnings = []
    text_data = scene_data.get("text", {})
    lens_data = text_data.get("lens", {})

    # Check for missing lens variants
    for lens in ["believer", "skeptic", "haunted"]:
        if lens not in lens_data or not lens_data[lens]:
            warnings.append(f"Missing lens variant: '{lens}'. Consider adding specific text for this archetype.")

    # Check for sensory details (rudimentary check)
    base_text = text_data.get("base", "").lower()
    sensory_keywords = ["smell", "sound", "hear", "see", "taste", "feel", "cold", "hot", "dark", "light", "metallic", "blood", "shadow"]
    if not any(w in base_text for w in sensory_keywords):
        warnings.append("Base text may lack sensory details. Consider adding smell, sound, or tactile descriptions.")

    return warnings

def preview_scene(filepath, lens_str="neutral", skills=None):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            scene_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return

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

def validate_file(filepath):
    validator = SchemaValidator()
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Determine type based on fields or assume scene
        valid, errors = validator.validate_scene(data)

        if valid:
            print(f"{Colors.GREEN}Validation Passed{Colors.RESET}")

            # Run style check
            warnings = check_style(data)
            if warnings:
                print(f"\n{Colors.YELLOW}Style Suggestions:{Colors.RESET}")
                for w in warnings:
                    print(f" - {w}")
            else:
                print(f"{Colors.GREEN}Style Check Passed{Colors.RESET}")

        else:
            print(f"{Colors.RED}Validation Failed:{Colors.RESET}")
            for err in errors:
                print(f" - {err}")

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

    print("\nLens Text (Press Enter to skip)")
    for lens in ["believer", "skeptic", "haunted"]:
        text = input(f"{lens.capitalize()}: ")
        if text:
            scene_data["text"]["lens"][lens] = text

    print("\nAdd an Insert? (y/n)")
    if input().lower().startswith('y'):
        insert_text = input("Insert Text: ")
        skill = input("Required Skill (e.g. Logic): ")
        level = input("Skill Level (e.g. 4): ")
        position = input("Position (AFTER_BASE, AFTER_LENS, BEFORE_CHOICES): ")

        insert = {
            "text": insert_text,
            "condition": {"skill_gte": {skill: int(level)}},
            "insert_at": position or "AFTER_LENS"
        }
        scene_data["text"]["inserts"].append(insert)

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
    p_preview.add_argument("--lens", default="neutral", choices=["neutral", "believer", "skeptic", "haunted"])
    p_preview.add_argument("--skills", help="Comma-separated skills (e.g. Logic:5,Perception:2)")

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
        preview_scene(args.file, args.lens, skills)
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
