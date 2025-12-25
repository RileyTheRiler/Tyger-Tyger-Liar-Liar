import json
import os
import sys

def check_json(path):
    print(f"Checking {path}...")
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        return False
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print(f"SUCCESS: Loaded {len(data)} items.")
        return data
    except Exception as e:
        print(f"ERROR: JSON load failed: {e}")
        return False

# Check interrupt lines
interrupts = check_json("data/interrupt_lines.json")
if interrupts:
    # Check sample keys
    keys = ["Logic", "Empathy", "Hand-to-Hand Combat"]
    for k in keys:
        if k in interrupts:
            print(f"  Found skill: {k}")
        else:
            print(f"  WARNING: Missing skill key {k}")

# Check theory commentary
commentary = check_json("data/theory_commentary.json")
if commentary:
    pass
