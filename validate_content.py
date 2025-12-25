#!/usr/bin/env python3
"""
Content Validation CLI - Validates game content against schemas.

Usage:
    python validate_content.py              # Validate all content
    python validate_content.py --verbose    # Show detailed output
    python validate_content.py --quick      # Quick validation (no cross-refs)
    python validate_content.py --json       # Output as JSON
    python validate_content.py --fix        # Show fix suggestions
    python validate_content.py scenes       # Validate only scenes
    python validate_content.py clues        # Validate only clues
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from schema_validator import SchemaValidator


class ContentValidator:
    """Enhanced content validation with CLI support."""

    def __init__(self, content_dir: str = "data", schemas_dir: str = "schemas"):
        self.content_dir = content_dir
        self.schemas_dir = schemas_dir
        self.validator = SchemaValidator(schemas_dir)
        self.stats = defaultdict(lambda: {"total": 0, "valid": 0, "errors": 0})
        self.all_errors: Dict[str, List[str]] = {}
        self.all_warnings: List[str] = []
        self.suggestions: Dict[str, List[str]] = {}

    def validate_all(self, quick: bool = False) -> bool:
        """Run full validation on all content."""
        valid = True

        # Validate each content type
        content_types = {
            "scenes": "scene",
            "clues": "clue",
            "npcs": "npc",
            "conditions": "condition",
            "encounters": "encounter"
        }

        for subdir, schema_type in content_types.items():
            subdir_path = os.path.join(self.content_dir, subdir)
            if os.path.exists(subdir_path):
                type_valid = self._validate_directory(subdir_path, schema_type)
                valid = valid and type_valid

        # Check cross-references unless quick mode
        if not quick:
            ref_errors = self.validator.check_cross_references(self.content_dir)
            if ref_errors:
                valid = False
                self.all_errors["_cross_references"] = ref_errors

        # Run additional integrity checks
        self._check_integrity()

        return valid

    def validate_type(self, content_type: str) -> bool:
        """Validate a specific content type."""
        type_mapping = {
            "scenes": "scene",
            "scene": "scene",
            "clues": "clue",
            "clue": "clue",
            "npcs": "npc",
            "npc": "npc",
            "conditions": "condition",
            "condition": "condition",
            "encounters": "encounter",
            "encounter": "encounter"
        }

        schema_type = type_mapping.get(content_type.lower())
        if not schema_type:
            print(f"Unknown content type: {content_type}")
            return False

        subdir = content_type if content_type.endswith("s") else content_type + "s"
        subdir_path = os.path.join(self.content_dir, subdir)

        if not os.path.exists(subdir_path):
            print(f"Directory not found: {subdir_path}")
            return False

        return self._validate_directory(subdir_path, schema_type)

    def _validate_directory(self, dir_path: str, schema_type: str) -> bool:
        """Validate all JSON files in a directory."""
        valid = True

        for filename in os.listdir(dir_path):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(dir_path, filename)
            self.stats[schema_type]["total"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle array or single object
                objects = data if isinstance(data, list) else [data]

                for i, obj in enumerate(objects):
                    obj_valid, errors = self.validator.validate_object(obj, schema_type)
                    key = f"{filename}[{i}]" if len(objects) > 1 else filename

                    if not obj_valid:
                        valid = False
                        self.stats[schema_type]["errors"] += 1
                        self.all_errors[f"{schema_type}/{key}"] = errors
                        self._generate_suggestions(key, obj, errors)
                    else:
                        self.stats[schema_type]["valid"] += 1

                    # Additional type-specific checks
                    self._check_type_specific(schema_type, obj, key)

            except json.JSONDecodeError as e:
                valid = False
                self.stats[schema_type]["errors"] += 1
                self.all_errors[f"{schema_type}/{filename}"] = [f"JSON parse error: {e}"]
            except Exception as e:
                valid = False
                self.stats[schema_type]["errors"] += 1
                self.all_errors[f"{schema_type}/{filename}"] = [f"Error: {e}"]

        return valid

    def _check_type_specific(self, schema_type: str, obj: dict, key: str):
        """Run type-specific validation checks."""
        if schema_type == "scene":
            # Check for empty choices
            choices = obj.get("choices", [])
            if not choices:
                self.all_warnings.append(f"{key}: Scene has no choices (dead end?)")

            # Check for lens variants
            text = obj.get("text", {})
            if isinstance(text, dict) and "lens" not in text:
                self.all_warnings.append(f"{key}: Scene has no lens variants")

        elif schema_type == "clue":
            # Check for theory links
            if not obj.get("links_to_theories"):
                self.all_warnings.append(f"{key}: Clue has no theory links")

            # Check reliability
            reliability = obj.get("reliability", 1.0)
            if reliability < 0.3:
                self.all_warnings.append(f"{key}: Very low reliability ({reliability})")

        elif schema_type == "encounter":
            # Check for escape option
            options = obj.get("options", [])
            has_escape = any("escape" in opt.get("id", "").lower() or
                           "run" in opt.get("id", "").lower() or
                           "retreat" in opt.get("id", "").lower()
                           for opt in options)
            if not has_escape:
                self.all_warnings.append(f"{key}: Encounter has no obvious escape option")

    def _check_integrity(self):
        """Run integrity checks across all content."""
        # Check for orphaned content
        scenes_dir = os.path.join(self.content_dir, "scenes")
        if os.path.exists(scenes_dir):
            all_scenes = set()
            referenced_scenes = set()

            for filename in os.listdir(scenes_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(scenes_dir, filename), 'r') as f:
                            data = json.load(f)
                        scenes = data if isinstance(data, list) else [data]

                        for scene in scenes:
                            all_scenes.add(scene.get("id", filename))
                            for choice in scene.get("choices", []):
                                if choice.get("next_scene"):
                                    referenced_scenes.add(choice["next_scene"])
                    except:
                        pass

            orphans = all_scenes - referenced_scenes - {"scene_arrival"}  # Starting scene excluded
            if orphans:
                self.all_warnings.append(f"Potentially orphaned scenes: {orphans}")

    def _generate_suggestions(self, key: str, obj: dict, errors: List[str]):
        """Generate fix suggestions for errors."""
        suggestions = []

        for error in errors:
            if "Missing required field" in error:
                field = error.split(": ")[-1]
                if field == "id":
                    suggested_id = key.replace(".json", "").replace("[", "_").replace("]", "")
                    suggestions.append(f"Add 'id': '{suggested_id}'")
                elif field == "text":
                    suggestions.append("Add 'text': {'base': '...', 'lens': {...}}")

            elif "should be string" in error:
                suggestions.append(f"Convert the value to a string with quotes")

            elif "not in allowed values" in error:
                suggestions.append(f"Check schema for allowed enum values")

        if suggestions:
            self.suggestions[key] = suggestions

    def print_results(self, verbose: bool = False, show_suggestions: bool = False):
        """Print validation results."""
        print("\n" + "=" * 60)
        print("CONTENT VALIDATION RESULTS")
        print("=" * 60)

        # Print stats
        print("\nSummary:")
        total_files = 0
        total_valid = 0
        total_errors = 0

        for content_type, stats in sorted(self.stats.items()):
            total_files += stats["total"]
            total_valid += stats["valid"]
            total_errors += stats["errors"]
            status = "OK" if stats["errors"] == 0 else "ERRORS"
            print(f"  {content_type:12} {stats['valid']:3}/{stats['total']:3} valid [{status}]")

        print(f"\n  {'TOTAL':12} {total_valid:3}/{total_files:3} valid")

        # Print errors
        if self.all_errors:
            print("\n" + "-" * 60)
            print("ERRORS:")
            for key, errors in sorted(self.all_errors.items()):
                print(f"\n  {key}:")
                for error in errors:
                    print(f"    - {error}")

                if show_suggestions and key in self.suggestions:
                    print("    Suggestions:")
                    for sug in self.suggestions[key]:
                        print(f"      > {sug}")

        # Print warnings if verbose
        if verbose and self.all_warnings:
            print("\n" + "-" * 60)
            print("WARNINGS:")
            for warning in self.all_warnings:
                print(f"  - {warning}")

        # Final status
        print("\n" + "=" * 60)
        if self.all_errors:
            print("VALIDATION FAILED")
        else:
            print("VALIDATION PASSED")
        print("=" * 60)

    def to_json(self) -> dict:
        """Return results as JSON-serializable dict."""
        return {
            "valid": len(self.all_errors) == 0,
            "stats": dict(self.stats),
            "errors": self.all_errors,
            "warnings": self.all_warnings,
            "suggestions": self.suggestions
        }


def main():
    parser = argparse.ArgumentParser(
        description="Validate game content against JSON schemas"
    )
    parser.add_argument(
        "content_type",
        nargs="?",
        default=None,
        help="Specific content type to validate (scenes, clues, npcs, etc.)"
    )
    parser.add_argument(
        "--content-dir", "-d",
        default="data",
        help="Content directory (default: data)"
    )
    parser.add_argument(
        "--schemas-dir", "-s",
        default="schemas",
        help="Schemas directory (default: schemas)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including warnings"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick validation (skip cross-reference checks)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show fix suggestions for errors"
    )

    args = parser.parse_args()

    validator = ContentValidator(args.content_dir, args.schemas_dir)

    # Run validation
    if args.content_type:
        valid = validator.validate_type(args.content_type)
    else:
        valid = validator.validate_all(quick=args.quick)

    # Output results
    if args.json:
        print(json.dumps(validator.to_json(), indent=2))
    else:
        validator.print_results(verbose=args.verbose, show_suggestions=args.fix)

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
