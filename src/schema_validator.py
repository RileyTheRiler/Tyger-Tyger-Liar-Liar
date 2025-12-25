"""
Schema Validator - Validates game content against JSON Schema definitions.
Run at launch or as CI/test step to catch content errors early.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class SchemaValidator:
    """Validates game content files against JSON schemas."""

    def __init__(self, schemas_dir: str = None):
        self.schemas_dir = schemas_dir or self._find_schemas_dir()
        self.schemas: Dict[str, dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._load_schemas()

    def _find_schemas_dir(self) -> str:
        """Find the schemas directory relative to this file."""
        current = Path(__file__).parent.parent
        schemas_path = current / "schemas"
        if schemas_path.exists():
            return str(schemas_path)
        return "schemas"

    def _load_schemas(self):
        """Load all schema files from the schemas directory."""
        if not os.path.exists(self.schemas_dir):
            self.warnings.append(f"Schemas directory not found: {self.schemas_dir}")
            return

        for filename in os.listdir(self.schemas_dir):
            if filename.endswith(".schema.json"):
                schema_name = filename.replace(".schema.json", "")
                try:
                    with open(os.path.join(self.schemas_dir, filename), 'r') as f:
                        self.schemas[schema_name] = json.load(f)
                except Exception as e:
                    self.errors.append(f"Failed to load schema {filename}: {e}")

    def validate_object(self, obj: dict, schema_name: str) -> Tuple[bool, List[str]]:
        """
        Validate an object against a schema.
        Returns (is_valid, list_of_errors).

        Note: This is a simplified validator. For full JSON Schema support,
        integrate jsonschema library.
        """
        errors = []

        if schema_name not in self.schemas:
            return False, [f"Unknown schema: {schema_name}"]

        schema = self.schemas[schema_name]

        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in obj:
                errors.append(f"Missing required field: {field}")

        # Check property types
        properties = schema.get("properties", {})
        for field, value in obj.items():
            if field in properties:
                prop_schema = properties[field]
                field_errors = self._validate_field(field, value, prop_schema)
                errors.extend(field_errors)

        return len(errors) == 0, errors

    def _validate_field(self, field_name: str, value, prop_schema: dict) -> List[str]:
        """Validate a single field against its schema."""
        errors = []

        expected_type = prop_schema.get("type")

        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Field '{field_name}' should be string, got {type(value).__name__}")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"Field '{field_name}' should be integer, got {type(value).__name__}")
            elif expected_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field '{field_name}' should be number, got {type(value).__name__}")
            elif expected_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field '{field_name}' should be boolean, got {type(value).__name__}")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"Field '{field_name}' should be array, got {type(value).__name__}")
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(f"Field '{field_name}' should be object, got {type(value).__name__}")

        # Check enum
        if "enum" in prop_schema and value not in prop_schema["enum"]:
            errors.append(f"Field '{field_name}' value '{value}' not in allowed values: {prop_schema['enum']}")

        # Check pattern for strings
        if "pattern" in prop_schema and isinstance(value, str):
            import re
            if not re.match(prop_schema["pattern"], value):
                errors.append(f"Field '{field_name}' does not match pattern: {prop_schema['pattern']}")

        # Check minimum/maximum for numbers
        if isinstance(value, (int, float)):
            if "minimum" in prop_schema and value < prop_schema["minimum"]:
                errors.append(f"Field '{field_name}' value {value} below minimum {prop_schema['minimum']}")
            if "maximum" in prop_schema and value > prop_schema["maximum"]:
                errors.append(f"Field '{field_name}' value {value} above maximum {prop_schema['maximum']}")

        return errors

    def validate_scene(self, scene: dict) -> Tuple[bool, List[str]]:
        """Validate a scene object."""
        return self.validate_object(scene, "scene")

    def validate_clue(self, clue: dict) -> Tuple[bool, List[str]]:
        """Validate a clue object."""
        return self.validate_object(clue, "clue")

    def validate_theory(self, theory: dict) -> Tuple[bool, List[str]]:
        """Validate a theory object."""
        return self.validate_object(theory, "theory")

    def validate_npc(self, npc: dict) -> Tuple[bool, List[str]]:
        """Validate an NPC object."""
        return self.validate_object(npc, "npc")

    def validate_condition(self, condition: dict) -> Tuple[bool, List[str]]:
        """Validate a condition object."""
        return self.validate_object(condition, "condition")

    def validate_encounter(self, encounter: dict) -> Tuple[bool, List[str]]:
        """Validate an encounter object."""
        return self.validate_object(encounter, "encounter")

    def validate_content_directory(self, content_dir: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all content files in a directory.
        Returns (all_valid, {filename: [errors]}).
        """
        all_errors = {}
        all_valid = True

        if not os.path.exists(content_dir):
            return False, {"_directory": [f"Content directory not found: {content_dir}"]}

        # Define file patterns and their schema types
        patterns = {
            "scenes": "scene",
            "clues": "clue",
            "theories": "theory",
            "npcs": "npc",
            "conditions": "condition",
            "encounters": "encounter"
        }

        for subdir, schema_type in patterns.items():
            subdir_path = os.path.join(content_dir, subdir)
            if os.path.exists(subdir_path):
                for filename in os.listdir(subdir_path):
                    if filename.endswith(".json"):
                        filepath = os.path.join(subdir_path, filename)
                        try:
                            with open(filepath, 'r') as f:
                                data = json.load(f)

                            # Handle array of objects or single object
                            objects = data if isinstance(data, list) else [data]

                            for i, obj in enumerate(objects):
                                valid, errors = self.validate_object(obj, schema_type)
                                if not valid:
                                    key = f"{filename}[{i}]" if len(objects) > 1 else filename
                                    all_errors[key] = errors
                                    all_valid = False
                        except json.JSONDecodeError as e:
                            all_errors[filename] = [f"JSON parse error: {e}"]
                            all_valid = False
                        except Exception as e:
                            all_errors[filename] = [f"Error reading file: {e}"]
                            all_valid = False

        return all_valid, all_errors

    def check_cross_references(self, content_dir: str) -> List[str]:
        """
        Check that all cross-references between content are valid.
        Returns list of reference errors.
        """
        errors = []

        # Collect all IDs
        all_ids = {
            "scenes": set(),
            "clues": set(),
            "theories": set(),
            "npcs": set(),
            "conditions": set(),
            "encounters": set(),
            "locations": set()
        }

        # Collect IDs from all content files
        for content_type in all_ids.keys():
            subdir = os.path.join(content_dir, content_type)
            if os.path.exists(subdir):
                for filename in os.listdir(subdir):
                    if filename.endswith(".json"):
                        try:
                            with open(os.path.join(subdir, filename), 'r') as f:
                                data = json.load(f)
                            objects = data if isinstance(data, list) else [data]
                            for obj in objects:
                                if "id" in obj:
                                    all_ids[content_type].add(obj["id"])
                        except:
                            pass

        # Check references in scenes
        scenes_dir = os.path.join(content_dir, "scenes")
        if os.path.exists(scenes_dir):
            for filename in os.listdir(scenes_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(scenes_dir, filename), 'r') as f:
                            data = json.load(f)
                        scenes = data if isinstance(data, list) else [data]

                        for scene in scenes:
                            scene_id = scene.get("id", filename)

                            # Check next_scene references
                            for choice in scene.get("choices", []):
                                next_scene = choice.get("next_scene")
                                if next_scene and next_scene not in all_ids["scenes"]:
                                    errors.append(f"{scene_id}: references unknown scene '{next_scene}'")

                            # Check passive_clues references
                            for pc in scene.get("passive_clues", []):
                                clue_id = pc.get("clue_id")
                                if clue_id and clue_id not in all_ids["clues"]:
                                    errors.append(f"{scene_id}: references unknown clue '{clue_id}'")

                            # Check encounter_id
                            enc_id = scene.get("encounter_id")
                            if enc_id and enc_id not in all_ids["encounters"]:
                                errors.append(f"{scene_id}: references unknown encounter '{enc_id}'")
                    except:
                        pass

        return errors


def run_validation(content_dir: str = "data", schemas_dir: str = "schemas") -> bool:
    """
    Run full validation on game content.
    Returns True if all validations pass.
    """
    print("=" * 60)
    print("CONTENT VALIDATION")
    print("=" * 60)

    validator = SchemaValidator(schemas_dir)

    # Check schema loading
    if validator.errors:
        print("\nSchema loading errors:")
        for err in validator.errors:
            print(f"  - {err}")
        return False

    print(f"\nLoaded {len(validator.schemas)} schemas: {list(validator.schemas.keys())}")

    # Validate content
    valid, errors = validator.validate_content_directory(content_dir)

    if errors:
        print("\nValidation errors:")
        for filename, errs in errors.items():
            print(f"\n  {filename}:")
            for err in errs:
                print(f"    - {err}")
    else:
        print("\nAll content files passed validation.")

    # Check cross-references
    ref_errors = validator.check_cross_references(content_dir)
    if ref_errors:
        print("\nCross-reference errors:")
        for err in ref_errors:
            print(f"  - {err}")
        valid = False
    else:
        print("\nAll cross-references valid.")

    print("\n" + "=" * 60)
    print(f"VALIDATION {'PASSED' if valid else 'FAILED'}")
    print("=" * 60)

    return valid


if __name__ == "__main__":
    import sys
    content_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    schemas_dir = sys.argv[2] if len(sys.argv) > 2 else "schemas"
    success = run_validation(content_dir, schemas_dir)
    sys.exit(0 if success else 1)
