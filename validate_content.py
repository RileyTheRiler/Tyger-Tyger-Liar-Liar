"""
Content Validation CLI
Validates all JSON content (scenes, clues, theories, etc.) against schemas and cross-references.
"""

import os
import json
import sys
from src.schema_validator import SchemaValidator

def validate_directory(validator, directory, schema_type):
    print(f"\nScanning {directory} for {schema_type}...")
    valid_count = 0
    invalid_count = 0

    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return 0, 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    items = data if isinstance(data, list) else [data]

                    for item in items:
                        if validator.validate(item, schema_type):
                            valid_count += 1
                        else:
                            print(f"[FAIL] {filename}: Validation failed for ID '{item.get('id', 'unknown')}'")
                            invalid_count += 1

                except json.JSONDecodeError:
                    print(f"[FAIL] {filename}: Invalid JSON")
                    invalid_count += 1
                except Exception as e:
                    print(f"[FAIL] {filename}: {e}")
                    invalid_count += 1

    return valid_count, invalid_count

def validate_all():
    validator = SchemaValidator()
    total_valid = 0
    total_invalid = 0

    print("=== TYGER TYGER CONTENT VALIDATION ===")

    # 1. Scenes
    # Handle scenes.json specifically as it's a list
    print("\nScanning scenes.json...")
    try:
        with open('data/scenes/vertical_slice/slice.json', 'r') as f:
            scenes = json.load(f)
            for scene in scenes:
                if validator.validate(scene, "scene"):
                    total_valid += 1
                else:
                     print(f"[FAIL] Scene {scene.get('id')} invalid.")
                     total_invalid += 1
    except Exception as e:
        print(f"Could not load slice.json: {e}")
        total_invalid += 1

    # 2. Clues
    v, i = validate_directory(validator, "data/clues", "clue")
    total_valid += v
    total_invalid += i

    # 3. NPCs
    v, i = validate_directory(validator, "data/npcs", "npc")
    total_valid += v
    total_invalid += i

    # 4. Conditions
    v, i = validate_directory(validator, "data/conditions", "condition")
    total_valid += v
    total_invalid += i

    print("\n" + "="*40)
    print(f"SUMMARY: {total_valid} Valid, {total_invalid} Invalid")
    print("="*40)

    if total_invalid > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    # Ensure we can import from src
    sys.path.append(os.path.abspath("."))
    validate_all()
