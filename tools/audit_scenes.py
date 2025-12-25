
import json
import os
import sys

def audit_scenes(directory):
    print(f"Auditing scenes in {directory}...")
    issues = []

    # Recursively find json files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".json"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                continue

            # Handle both single scene object and list of scenes
            scenes = []
            if isinstance(data, list):
                scenes = data
            elif isinstance(data, dict):
                # Check if it's a scene file (has 'id' and 'text') or a wrapper (like vertical_slice.json might be)
                if 'id' in data and 'text' in data:
                    scenes = [data]
                else:
                    # Might be a config file or non-scene file
                    pass

            for scene in scenes:
                if not isinstance(scene, dict): continue

                scene_id = scene.get('id', 'unknown')
                text = scene.get('text')

                if not text:
                    continue

                # Check for lens variations
                if isinstance(text, dict):
                    lens = text.get('lens')
                    if not lens:
                         # It's okay if base text is simple, but we want to flag important scenes missing lens
                         # For now, just note it.
                         # issues.append(f"{file} :: {scene_id} - Missing 'lens' block entirely.")
                         pass
                    else:
                        missing_lenses = []
                        for archetype in ['believer', 'skeptic', 'haunted']:
                            if archetype not in lens:
                                missing_lenses.append(archetype)

                        if missing_lenses:
                            issues.append(f"{file} :: {scene_id} - Missing lens variations: {', '.join(missing_lenses)}")
                elif isinstance(text, str):
                    # Simple string text, definitely missing lens
                    # issues.append(f"{file} :: {scene_id} - Text is simple string, missing lens structure.")
                    pass

    if issues:
        print("\nFound issues:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\nNo missing lens variations found!")

if __name__ == "__main__":
    audit_scenes("data/scenes")
