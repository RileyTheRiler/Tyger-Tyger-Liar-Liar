#!/usr/bin/env python3
"""
Case Diagnostic Tool
Loads case files and analyzes their structure, theory links, and validity.
"""

import sys
import os
import json
from dataclasses import dataclass
from typing import List

# Mock Enums for standalone validation
class OutcomeType:
    ACCURATE = "ACCURATE"
    PARTIAL = "PARTIAL"
    FALSE = "FALSE"

def validate_case(filepath):
    print(f"\nAnalyzing: {filepath}")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
    except Exception as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return False

    all_valid = True
    for case in data:
        valid = True
        print(f"  Case: {case.get('title', 'Unknown Title')} (ID: {case.get('id', 'No ID')})")

        # Check required fields
        required = ["id", "title", "hook", "outcomes"]
        for req in required:
            if req not in case:
                print(f"    [ERROR] Missing required field: {req}")
                valid = False

        # Check theories
        theories = case.get("theories", [])
        if not theories:
             print("    [WARN] No theories defined for this case.")

        # Check outcomes
        outcomes = case.get("outcomes", [])
        if not outcomes:
            print("    [ERROR] No outcomes defined.")
            valid = False

        theory_usage = {t: 0 for t in theories}

        for out in outcomes:
            out_id = out.get("id")
            req_theory = out.get("required_theory")

            if not req_theory:
                 print(f"    [ERROR] Outcome '{out_id}' missing required_theory.")
                 valid = False
            elif req_theory not in theories:
                 print(f"    [ERROR] Outcome '{out_id}' references unknown theory '{req_theory}'.")
                 valid = False
            else:
                 theory_usage[req_theory] += 1

            if "type" not in out:
                 print(f"    [ERROR] Outcome '{out_id}' missing type.")
                 valid = False

        # Check for unused theories
        for t, count in theory_usage.items():
            if count == 0:
                print(f"    [WARN] Theory '{t}' is defined but leads to no outcome.")

        if valid:
            print(f"    [PASS] Case '{case.get('id')}' structure is valid.")
        else:
            all_valid = False

    return all_valid

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/analyze_case.py <path_to_case_json> or <directory>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith(".json"):
                     validate_case(os.path.join(root, file))
    else:
        validate_case(target)
